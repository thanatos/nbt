import collections

import six as _six


class Tag(object):
    pass


class _SimpleTag(Tag):
    def __init__(self, value):
        self._value = self._validate(value)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = self._validate(value)

    value = property(_get_value, _set_value)
    del _get_value
    del _set_value


class NumericTag(_SimpleTag):
    def _validate(self, value):
        value = int(value)
        if value < self._MIN or self._MAX < value:
            raise ValueError(
                '{0}\'s value must be an integer in the range'
                ' [{1}, {2}].'.format(
                    self.__class__.__name__, self._MIN, self._MAX))
        return value


class ByteTag(NumericTag):
    _MIN = 0
    _MAX = 255

class ShortTag(NumericTag):
    _MIN = -(2 ** 15)
    _MAX = 2 ** 15 - 1

class IntTag(NumericTag):
    _MIN = -(2 ** 31)
    _MAX = 2 ** 31 - 1

class LongTag(NumericTag):
    _MIN = -(2 ** 63)
    _MAX = 2 ** 63 - 1


class FloatTag(_SimpleTag):
    def _validate(self, value):
        value = float(value)
        return value


class DoubleTag(_SimpleTag):
    def _validate(self, value):
        value = float(value)
        return value


class ByteArrayTag(_SimpleTag):
    def _validate(self, value):
        value = bytearray(value)
        return value


class StringTag(_SimpleTag):
    def _validate(self, value):
        value = _six.text_type(value)
        return value


class _ListLikeTag(Tag, collections.MutableSequence):
    def __init__(self, values):
        self._value = []
        for value in values:
            self._value.append(self._validate(value))

    def __iter__(self):
        for i in self._value:
            yield i

    def __len__(self):
        return len(self._value)

    def __getitem__(self, index):
        return self._value[index]

    def __setitem__(self, index, value):
        value = self._validate(value)
        self._value[index] = value

    def __delitem__(self, index):
        del self._value[index]

    def insert(self, index, item):
        value = self._validate(item)
        self._value.insert(index, value)


class ListTag(_ListLikeTag):
    def __init__(self, tag_type, tags=()):
        self._tag_type = tag_type
        super(ListTag, self).__init__(tags)

    @property
    def tag_type(self):
        return self._tag_type

    def _validate(self, value):
        if not isinstance(value, self._tag_type):
            raise TypeError('This ListTag contains {0}.'.format(self._tag_type))
        return value


class IntArrayTag(_ListLikeTag):
    def __init__(self, ints=()):
        super(IntArrayTag, self).__init__(ints)

    def _validate(self, value):
        value = int(value)
        if value < -(2 ** 31) or (2 ** 31 - 1) < value:
            raise ValueError(
                '{0}\'s can only hold ints in the range of signed 32-bit'
                ' integer values.'.format(self.__class__.__name__))
        return value


class CompoundTag(Tag, collections.MutableMapping):
    def __init__(self, value={}):
        self._value = {}
        for k, v in value:
            self[k] = v

    def __len__(self):
        return len(self._value)

    def __iter__(self):
        return iter(self._value)

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, value):
        key = _six.text_type(key)
        if not isinstance(value, Tag):
            raise TypeError('CompoundTags can only hold tags as values.')
        self._value[key] = value

    def __delitem__(self, key):
        del self._value[key]


__all__ = [
    'ByteTag',
    'ShortTag',
    'IntTag',
    'LongTag',
    'FloatTag',
    'DoubleTag',
    'ByteArrayTag',
    'StringTag',
    'ListTag',
    'IntArrayTag',
    'CompoundTag',
]
