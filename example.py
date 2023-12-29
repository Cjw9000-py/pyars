from pyars import *

@arguments
class BuildArguments:
    projects: set[str] = positional(nargs='+', help="The projects you want to use")
    root: Path = flag(extra_opts='--root-path', default='cwd', help="The root dir to use")
    verbose: bool = switch(help_suffix="verbose output")
    parallel: int = flag(nargs='?', type=int, default=1, help="Number of concurrent tasks to run")
    colorize_output: bool = switch(name='colorize', help_suffix="colorized console output")

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
        extra={
            'your-mom': BuildArguments
        }
    )

def main() -> None:
    parsed_args = ConsoleArguments.parse_args([
        'some/root', 'build', 'proj1', 'proj2', '--verbose', '--colorize', '--root', 'my-root'
    ])
    print(parsed_args)

if __name__ == "__main__":
    main()
