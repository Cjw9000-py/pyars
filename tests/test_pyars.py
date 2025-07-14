from pathlib import Path
import pytest

from pyars import arguments, positional, flag, switch, command, Arguments, InvalidArgumentsError


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


def test_switch_conflict():
    argv = ['proj', '--verbose', '--no-verbose']
    with pytest.raises(InvalidArgumentsError):
        BuildArguments.parse_args(argv)
