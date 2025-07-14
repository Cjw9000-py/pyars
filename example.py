"""Example demonstrating basic usage of :mod:`pyars`."""

from pyars import *

@arguments
class BuildArguments:
    """Arguments for the ``build`` command."""
    projects: set[str] = positional(nargs='+', help="The projects you want to use")
    root: Path = flag(extra_opts='--root-path', default='cwd', help="The root dir to use")
    verbose: bool = switch(help_suffix="verbose output")
    parallel: int = flag(nargs='?', type=int, default=1, help="Number of concurrent tasks to run")
    colorize_output: bool = switch(name='colorize', help_suffix="colorized console output")

@arguments
class CleanArguments:
    """Arguments for the ``clean`` command."""
    include_subdirs: bool = switch(help_suffix='Clean subdirectories as well')
    force: bool = switch(help_suffix='Force cleaning, even if up-to-date')

@arguments
class ConsoleArguments:
    """Top-level arguments for the console application."""
    root: Path
    command: Arguments = command(
        extra={},
        build=BuildArguments,
        clean=CleanArguments,
    )

def main() -> None:
    """Entry point for running the example."""
    parsed_args = ConsoleArguments.parse_args([
        'some/root', 'build', 'proj1', 'proj2', '--verbose', '--colorize', '--root', 'my-root'
    ])
    print(parsed_args)

if __name__ == "__main__":
    main()
