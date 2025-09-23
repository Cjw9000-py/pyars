"""Example demonstrating basic usage of :mod:`pyars` with the new API."""

from pathlib import Path

from pyars import arguments, positional, option, flag, command, Arguments


@arguments
class BuildArguments:
    """Arguments for the ``build`` command."""

    targets: set[str] = positional(nargs='+', help='Targets to build')
    root: Path = option('-r', '--root', convert=Path, default='.')
    verbose: bool = flag('-v', help='Enable verbose output')


@arguments
class CleanArguments:
    """Arguments for the ``clean`` command."""

    force: bool = flag(help='Force cleaning even if up-to-date')


@arguments
class ConsoleArguments:
    """Top-level arguments for the console application."""

    root: Path
    command: Arguments = command(
        build=BuildArguments,
        clean=CleanArguments,
    )


def main() -> None:
    """Entry point for running the example."""
    parsed_args = ConsoleArguments.parse_args([
        'workspace', 'build', 'proj1', 'proj2', '--root', '/tmp/output', '--verbose'
    ])
    print(parsed_args)


if __name__ == '__main__':
    main()
