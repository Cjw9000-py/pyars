from pathlib import Path

import pytest

from pyars import (
    arguments,
    positional,
    option,
    flag,
    command,
    Arguments,
)


@arguments
class BuildArguments:
    targets: set[str] = positional(nargs='+', help='Targets to build')
    root: Path = option('-r', convert=Path, default='.')
    verbose: bool = flag('-v', help='Enable verbose output')


@arguments
class CleanArguments:
    force: bool = flag(help='Force cleaning even if up-to-date')


@arguments
class ConsoleArguments:
    root: Path
    command: Arguments = command(
        build=BuildArguments,
        clean=CleanArguments,
    )


def test_build_defaults():
    args = BuildArguments.parse_args(['proj1'])
    assert args.targets == {'proj1'}
    assert args.root == Path('.')
    assert args.verbose is False


def test_build_option_and_flag_aliases():
    args = BuildArguments.parse_args(['proj1', '-r', '/tmp/output', '--verbose'])
    assert args.targets == {'proj1'}
    assert args.root == Path('/tmp/output')
    assert args.verbose is True


def test_flag_without_explicit_names():
    @arguments
    class Sample:
        clean: bool = flag(help='perform cleanup')

    parsed = Sample.parse_args(['--clean'])
    assert parsed.clean is True
    parsed = Sample.parse_args([])
    assert parsed.clean is False


def test_console_build_command():
    args = ConsoleArguments.parse_args(['workspace', 'build', 'proj1', 'proj2'])
    assert args.root == Path('workspace')
    assert isinstance(args.command, BuildArguments)
    assert args.command.targets == {'proj1', 'proj2'}


def test_missing_command_exits():
    with pytest.raises(SystemExit):
        ConsoleArguments.parse_args(['workspace'])


def test_clean_command_flag():
    args = ConsoleArguments.parse_args(['ws', 'clean', '--force'])
    assert isinstance(args.command, CleanArguments)
    assert args.command.force is True
