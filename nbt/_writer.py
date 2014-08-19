import contextlib as _contextlib
import gzip as _gzip
import struct as _struct

import six as _six

from . import _constants
from . import _tag


def _write_simple_tag_payload(stream, tag):
    simple_tags = {
        _tag.ByteTag: 'b',
        _tag.ShortTag: 'h',
        _tag.IntTag: 'i',
        _tag.LongTag: 'q',
        _tag.FloatTag: 'f',
        _tag.DoubleTag: 'd',
    }
    if tag.__class__ in simple_tags:
        format = '>{0}'.format(simple_tags[tag.__class__])
        stream.write(_struct.pack(format, tag.value))
    elif isinstance(tag, _tag.ByteArrayTag):
        stream.write(_struct.pack('>I', len(value)))
        stream.write(value)
    elif isinstance(tag, _tag.StringTag):
        value = tag.value.encode('utf-8')
        stream.write(_struct.pack('>H', len(value)))
        stream.write(value)
    elif isinstance(tag, _tag.ListTag):
        raise AssertionError(
            '_write_simple_tag_payload should not be called for ListTags.')
    elif isinstance(tag, _tag.CompoundTag):
        raise AssertionError(
            '_write_simple_tag_payload should not be called for CompoundTags.')
    elif isinstance(tag, _tag.IntArrayTag):
        stream.write(_struct.pack('>I', len(tag)))
        stream.write(b''.join(_struct.pack('>i', i) for i in tag))
    else:
        raise IOError('Unknown tag type "{0}"!'.format(tag.__class__))


def _write_named_tag_header(stream, tag_type, name):
    tag_header = _struct.pack(
        '>BH', _constants.TAG_CLASS_TO_TYPE[tag_type], len(name))
    tag_header += name.encode('utf-8')
    stream.write(tag_header)


def _deal_with_tag(stream, tag, stack):
    if isinstance(tag, _tag.CompoundTag):
        stack.append((tag, tag.iteritems()))
    elif isinstance(tag, _tag.ListTagBase):
        stack.append((tag, iter(tag)))
        list_tag_header = _struct.pack(
            '>BI', _constants.TAG_CLASS_TO_TYPE[tag.tag_type], len(tag))
        stream.write(list_tag_header)
    else:
        _write_simple_tag_payload(stream, tag)


def write_tag(stream, tag, root_name=_six.u('')):
    if not isinstance(tag, _tag.CompoundTag):
        raise ValueError('Can only write CompoundTags as the root tag!')

    _write_named_tag_header(stream, tag.__class__, root_name)
    
    tag_stack = []
    _deal_with_tag(stream, tag, tag_stack)

    while tag_stack:
        top = tag_stack[-1]
        try:
            value = top[1].next()
        except StopIteration:
            tag_stack.pop()
            if isinstance(top[0], _tag.CompoundTag):
                stream.write(b'\x00')
            continue

        if isinstance(top[0], _tag.CompoundTag):
            key, tag = value
            _write_named_tag_header(stream, tag.__class__, key)
        else:
            tag = value
        _deal_with_tag(stream, tag, tag_stack)


def write_file(filename, tag, root_name=_six.u('')):
    with open(filename, 'wb') as fh:
        write_tag(fh, tag, root_name)


def write_compressed_file(filename, tag, root_name=_six.u('')):
    with _contextlib.closing(_gzip.open(filename, 'wb')) as gh:
        write_tag(gh, tag, root_name)


__all__ = [
    'write_tag',
    'write_file',
    'write_compressed_file',
]
