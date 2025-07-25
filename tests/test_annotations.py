from __future__ import annotations
from pathlib import Path

from pyars import arguments, positional, flag, switch


@arguments
class StringArgs:
    value: 'Path'
    count: 'int' = flag()
    verbose: 'bool' = switch()


def test_string_annotations_parsing():
    argv = ['folder', '--count', '3', '--verbose']
    parsed = StringArgs.parse_args(argv)
    assert parsed.value == Path('folder')
    assert parsed.count == 3
    assert parsed.verbose is True


@arguments
class UnknownArgs:
    stuff: 'Unknown'


def test_unknown_annotation_graceful():
    argv = ['x']
    parsed = UnknownArgs.parse_args(argv)
    assert parsed.stuff == 'x'


@arguments
class GenericArgs:
    names: 'list[str]' = positional(nargs='+')


def test_generic_string_annotation():
    argv = ['a', 'b']
    parsed = GenericArgs.parse_args(argv)
    assert parsed.names == ['a', 'b']
