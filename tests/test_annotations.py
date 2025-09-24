from __future__ import annotations
from pathlib import Path

from pyars import arguments, positional, option, flag


class Unknown(str):
    """Sentinel type used to exercise forward reference handling."""


@arguments
class StringArgs:
    value: 'Path'
    count: 'int' = option('--count')
    verbose: 'bool' = flag()


def test_string_annotations_parsing():
    argv = ['folder', '--count', '3', '--verbose']
    parsed = StringArgs.parse_args(argv)
    assert parsed.value == Path('folder')
    assert parsed.count == 3
    assert parsed.verbose is True


@arguments
class UnknownArgs:
    stuff: 'Unknown' = positional()


def test_unknown_annotation_graceful():
    argv = ['x']
    parsed = UnknownArgs.parse_args(argv)
    assert parsed.stuff == 'x'


@arguments
class CollectionArgs:
    names: 'set[str]' = positional(nargs='+')


def test_collection_annotation():
    argv = ['a', 'b']
    parsed = CollectionArgs.parse_args(argv)
    assert parsed.names == {'a', 'b'}
