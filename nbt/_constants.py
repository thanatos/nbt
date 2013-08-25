import six as _six

from . import _tag


TAG_TYPE_END = 0
TAG_TYPE_BYTE = 1
TAG_TYPE_SHORT = 2
TAG_TYPE_INT = 3
TAG_TYPE_LONG = 4
TAG_TYPE_FLOAT = 5
TAG_TYPE_DOUBLE = 6
TAG_TYPE_BYTE_ARRAY = 7
TAG_TYPE_STRING = 8
TAG_TYPE_LIST = 9
TAG_TYPE_COMPOUND = 10
TAG_TYPE_INT_ARRAY = 11


TAG_TYPE_TO_CLASS = {
    TAG_TYPE_BYTE: _tag.ByteTag,
    TAG_TYPE_SHORT: _tag.ShortTag,
    TAG_TYPE_INT: _tag.IntTag,
    TAG_TYPE_LONG: _tag.LongTag,
    TAG_TYPE_FLOAT: _tag.FloatTag,
    TAG_TYPE_DOUBLE: _tag.DoubleTag,
    TAG_TYPE_BYTE_ARRAY: _tag.ByteArrayTag,
    TAG_TYPE_STRING: _tag.StringTag,
    TAG_TYPE_LIST: _tag.ListTag,
    TAG_TYPE_COMPOUND: _tag.CompoundTag,
    TAG_TYPE_INT_ARRAY: _tag.IntArrayTag,
}
TAG_CLASS_TO_TYPE = dict((v, k) for k, v in _six.iteritems(TAG_TYPE_TO_CLASS))
ALL_TAG_TYPES = set(TAG_TYPE_TO_CLASS)
ALL_TAG_TYPES.add(TAG_TYPE_END)


def _tag_type_repr(tag_type):
    tag_names = {
        TAG_TYPE_END: 'TAG_TYPE_END',
        TAG_TYPE_BYTE: 'TAG_TYPE_BYTE',
        TAG_TYPE_SHORT: 'TAG_TYPE_SHORT',
        TAG_TYPE_INT: 'TAG_TYPE_INT',
        TAG_TYPE_LONG: 'TAG_TYPE_LONG',
        TAG_TYPE_FLOAT: 'TAG_TYPE_FLOAT',
        TAG_TYPE_DOUBLE: 'TAG_TYPE_DOUBLE',
        TAG_TYPE_BYTE_ARRAY: 'TAG_TYPE_BYTE_ARRAY',
        TAG_TYPE_STRING: 'TAG_TYPE_STRING',
        TAG_TYPE_LIST: 'TAG_TYPE_LIST',
        TAG_TYPE_COMPOUND: 'TAG_TYPE_COMPOUND',
        TAG_TYPE_INT_ARRAY: 'TAG_TYPE_INT_ARRAY',
    }
    if tag_type in tag_names:
        return 'nbt.{0}'.format(tag_names[tag_type])
    else:
        return repr(tag_type)


__all__ = [
    'TAG_TYPE_END',
    'TAG_TYPE_BYTE',
    'TAG_TYPE_SHORT',
    'TAG_TYPE_INT',
    'TAG_TYPE_LONG',
    'TAG_TYPE_FLOAT',
    'TAG_TYPE_DOUBLE',
    'TAG_TYPE_BYTE_ARRAY',
    'TAG_TYPE_STRING',
    'TAG_TYPE_LIST',
    'TAG_TYPE_COMPOUND',
    'TAG_TYPE_INT_ARRAY',
]
