import array as _array
import contextlib as _contextlib
import gzip as _gzip
import struct as _struct

from . import _constants
from . import _tag


class _EofReportingStream(object):
    def __init__(self, stream):
        self._stream = stream

    def read(self, size):
        data = self._stream.read(size)
        if len(data) != size:
            raise IOError('Unexpected EOF.')
        return data


def _read_tag_header(stream):
    data = stream.read(1)
    tag_type = ord(data[0])
    if tag_type == _constants.TAG_TYPE_END:
        return tag_type, None
    tag_name_length = _struct.unpack('>H', stream.read(2))[0]
    if tag_name_length:
        tag_name = stream.read(tag_name_length).decode('utf-8')
    else:
        tag_name = u''
    return tag_type, tag_name


def _read_simple_payload(tag_type, stream):
    # type -> (unpack_format, payload_length)
    simple_payloads = {
        _constants.TAG_TYPE_BYTE: ('>b', 1),
        _constants.TAG_TYPE_SHORT: ('>h', 2),
        _constants.TAG_TYPE_INT: ('>i', 4),
        _constants.TAG_TYPE_LONG: ('>q', 8),
        _constants.TAG_TYPE_FLOAT: ('>f', 4),
        _constants.TAG_TYPE_DOUBLE: ('>d', 8),
    }
    if tag_type in simple_payloads:
        format, length = simple_payloads[tag_type]
        value = _struct.unpack(format, stream.read(length))[0]
        cls = _constants.TAG_TYPE_TO_CLASS[tag_type]
        return cls(value)
    elif tag_type == _constants.TAG_TYPE_BYTE_ARRAY:
        length = _struct.unpack('>I', stream.read(4))[0]
        # N.b., a bytearray implies that the bytes are unsigned. The Wiki
        # however, is confused: it says they're signed, but implies them to be
        # both. (Block IDs are encoded as a TAG_Byte_Array, they have values of
        # [0, 255]. But Biomes supposedly have values [-1, 22]. So, we've got
        # more values than we have bits for. We assume biomes is messed up, and
        # -1, which is "uncalculated" is really 255.
        return _tag.ByteArrayTag(bytearray(stream.read(length)))
    elif tag_type == _constants.TAG_TYPE_STRING:
        length = _struct.unpack('>H', stream.read(2))[0]
        return _tag.StringTag(stream.read(length).decode('utf-8'))
    elif tag_type == _constants.TAG_TYPE_LIST:
        raise AssertionError(
            '_read_simple_payload should not be called for TAG_TYPE_LIST.')
    elif tag_type == _constants.TAG_TYPE_COMPOUND:
        raise AssertionError(
            '_read_simple_payload should not be called for TAG_TYPE_COMPOUND.')
    elif tag_type == _constants.TAG_TYPE_INT_ARRAY:
        length = _struct.unpack('>I', stream.read(4))[0]
        data = stream.read(4 * length)
        return _tag.IntArrayTag(
            _struct.unpack('>i', data[x*4:x*4+4])[0] for x in xrange(length))
    else:
        raise IOError('Unknown tag type!')


def _process_tag_payload(stream, tag_type, stack):
    if tag_type == _constants.TAG_TYPE_COMPOUND:
        stack.append(_TagStackCompound())
        return None
    elif tag_type == _constants.TAG_TYPE_LIST:
        inner_type, length = _struct.unpack('>BI', stream.read(5))
        stack.append(_TagStackList(inner_type, length))
        return None
    elif tag_type == _constants.TAG_TYPE_END:
        raise IOError('Attempted to read a payload for TAG_TYPE_END!')
    elif tag_type in _constants.ALL_TAG_TYPES:
        return _read_simple_payload(tag_type, stream)
    else:
        raise IOError(
            'Attempted to read a payload for unknown tag type {0}.'.format(
                tag_type))


def _read_loop(stream, stack):
    while True:
        top = stack[-1]
        read_tag_type, returned_value = top.process(stream)
        if read_tag_type is not None:
            value = _process_tag_payload(stream, read_tag_type, stack)
            if value is not None:
                top.process_value(value)
        else:
            stack.pop()
            if not stack:
                return returned_value
            else:
                stack[-1].process_value(returned_value)


class _TagStackBase(object):
    def process(self, stream):
        raise NotImplementedError()

    def process_value(self, value):
        raise NotImplementedError()


class _TagStackList(_TagStackBase):
    def __init__(self, inner_tag_type, length):
        # TODO: check inner_type
        self._length = length
        self._items_read = 0
        self._inner_tag_type = inner_tag_type
        inner_tag_class = _constants.TAG_TYPE_TO_CLASS[inner_tag_type]
        self._value = _tag.ListTag(inner_tag_class)

    def process(self, stream):
        if self._items_read == self._length:
            return None, self._value
        else:
            return self._inner_tag_type, None

    def process_value(self, value):
        self._value.append(value)
        self._items_read += 1


class _TagStackCompound(_TagStackBase):
    def __init__(self):
        self._value = _tag.CompoundTag()
        self._tag_name = None

    def process(self, stream):
        tag_type, tag_name = _read_tag_header(stream)
        if tag_type == _constants.TAG_TYPE_END:
            return None, self._value
        else:
            self._tag_name = tag_name
            return tag_type, None

    def process_value(self, value):
        if self._tag_name is None:
            raise AssertionError('_TagStackCompound called with value'
                                 ' unexpectedly.')
        self._value[self._tag_name] = value


def read_tag(stream):
    eof_stream = _EofReportingStream(stream)
    
    tag_type, name = _read_tag_header(eof_stream)
    if tag_type != _constants.TAG_TYPE_COMPOUND:
        raise IOError('Root tag was not a compound tag!')

    stack = []
    ret = _process_tag_payload(eof_stream, tag_type, stack)
    if ret is not None:
        return name, ret

    return name, _read_loop(eof_stream, stack)


def read_file(filename):
    with open(filename, 'rb') as fh:
        return read_tag(fh)


def read_compressed_file(filename):
    with _contextlib.closing(_gzip.open(filename, 'rb')) as fh:
        return read_tag(fh)


__all__ = [
    'read_tag',
    'read_file',
    'read_compressed_file',
]
