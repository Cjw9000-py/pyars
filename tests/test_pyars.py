from pathlib import Path
from enum import Enum
from argparse import ArgumentParser
import pytest

from pyars import (
    arguments,
    positional,
    flag,
    switch,
    command,
    enum,
    list_argument,
    Arguments,
)


@arguments
class BuildArguments:
    projects: set[str] = positional(nargs='+')
    root: Path = flag(extra_opts='--root-path', default='cwd')
    verbose: bool = switch(help_suffix='verbose output')
    parallel: int = flag(nargs='?', type=int, default=1)
    colorize_output: bool = switch(name='colorize', help_suffix='colorized console output')


def test_build_parse_all_options():
    argv = [
        'proj1',
        'proj2',
        '--root', 'my-root',
        '--parallel', '2',
        '--verbose',
        '--colorize',
    ]
    parsed = BuildArguments.parse_args(argv)
    assert parsed.projects == {'proj1', 'proj2'}
    assert parsed.root == Path('my-root')
    assert parsed.verbose is True
    assert parsed.parallel == 2
    assert parsed.colorize_output is True


def test_build_parse_defaults():
    argv = ['proj1']
    parsed = BuildArguments.parse_args(argv)
    assert parsed.projects == {'proj1'}
    assert parsed.root == Path('cwd')
    assert parsed.verbose is False
    assert parsed.parallel == 1
    assert parsed.colorize_output is False


@arguments
class CleanArguments:
    include_subdirs: bool = switch(help_suffix='Clean subdirectories as well')
    force: bool = switch(help_suffix='Force cleaning, even if up-to-date')


@arguments
class ConsoleArguments:
    root: Path
    command: Arguments = command(
        build=BuildArguments,
        clean=CleanArguments,
    )


class Mode(Enum):
    debug = 1
    release = 2


@arguments
class ExtraArguments:
    mode: Mode = enum(Mode)
    tags: list[str] = list_argument(env_var='EXTRA_TAGS', container=list)


@arguments
class EnvArguments:
    count: int = flag(type=int, env_var='COUNT_VAR')
    enabled: bool = switch(env_var='SWITCH_VAR')


def test_enum_argument():
    argv = ['--mode', 'debug', '--tags', 'x']
    parsed = ExtraArguments.parse_args(argv)
    assert parsed.mode is Mode.debug


def test_list_argument_with_env_default(monkeypatch):
    monkeypatch.setenv('EXTRA_TAGS', 'a,b,c')
    parsed = ExtraArguments.parse_args(['--mode', 'release'])
    assert parsed.tags == ['a', 'b', 'c']


def test_env_defaults(monkeypatch):
    monkeypatch.setenv('COUNT_VAR', '7')
    monkeypatch.setenv('SWITCH_VAR', 'true')
    parsed = EnvArguments.parse_args([])
    assert parsed.count == 7
    assert parsed.enabled is True


def test_command_build():
    argv = [
        'some/root',
        'build',
        'proj1',
        '--verbose',
        '--colorize',
    ]
    parsed = ConsoleArguments.parse_args(argv)
    assert parsed.root == Path('some/root')
    assert isinstance(parsed.command, BuildArguments)
    assert parsed.command.projects == {'proj1'}
    assert parsed.command.verbose is True
    assert parsed.command.colorize_output is True


def test_command_clean():
    argv = [
        'root',
        'clean',
        '--force',
    ]
    parsed = ConsoleArguments.parse_args(argv)
    assert isinstance(parsed.command, CleanArguments)
    assert parsed.command.force is True


@arguments
class NoneDefaultArguments:
    flag_arg: str | None = flag(default=None)


def test_flag_default_none_optional():
    parsed = NoneDefaultArguments.parse_args([])
    assert parsed.flag_arg is None
    
def test_new_parser_callback_and_kwargs():
    captured: list[ArgumentParser] = []

    def customize(parser: ArgumentParser) -> None:
        captured.append(parser)
        parser.add_argument('--extra', action='store_true')

    parser = BuildArguments.new_parser(callbacks=customize, description='desc')
    assert parser.description == 'desc'
    namespace = parser.parse_args(['proj', '--extra'])
    assert captured[0] is parser
    assert namespace.extra is True
    
    
def test_switch_conflict():
    argv = ['proj', '--verbose', '--no-verbose']
    with pytest.raises(InvalidArgumentsError):
        BuildArguments.parse_args(argv)
