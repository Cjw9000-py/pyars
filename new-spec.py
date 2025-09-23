
"""
This is how I want this library to work. DO NOT ALTER THIS FILE!
"""

from pathlib import Path
from pyars import (
    arguments,  # the main decorator
    positional,  # for positional arguments
    option,      # for --something <value> or -s <value> cmd options
    flag,        # A boolean flag, different from before
    command,     # works like before, allows for a command argument
    Arguments,   # for type hinting
)


@arguments
class BuildArguments:
    targets: set[str] = positional(nargs='+', help='The targets you want to compile')
    root: Path = option('-r', convert=Path, default='.')   # this would convert the value to a Path class, including the default value
    verbose: bool = flag('-v', default=False)

@arguments
class CleanArguments:
    """Arguments for the ``clean`` command."""
    force: bool = flag(help='Force cleaning, even if up-to-date')

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
    args = ConsoleArguments.parse_args([
        'some/root', 'build', 'proj1', 'proj2', '--verbose', '--root', 'my-root'
    ])
    print(args)

if __name__ == "__main__":
    main()
