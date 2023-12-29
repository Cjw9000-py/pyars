from .impl import (
    arguments,
    CommandArgument as command,
    PositionalArgument as positional,
    FlagArgument as flag,
    SwitchArgument as switch,
    ArgumentContainer as Arguments
)

from pathlib import Path


__all__ = [
    'arguments',
    'command',
    'positional',
    'flag',
    'switch',
    'Arguments',
    'Path',
]

# can you make this example more professional?
# please keep the pyars module and use its contents exactly like in this example.
# but change the example so that more and new arguments are demonstrated and
# the example itself seems more realistic
#
# from __future__ import annotations
# from pyars import *
# from attrs import define, field
# from pathlib import Path
# @arguments
# class BuildArguments:
#     projects: set[str] = positional(nargs='+', help='The projects you want to use')
#     root: Path = flag(extra_opts='--root-path', default='cwd', help='The root dir to use')
#     cool: bool = switch(help_suffix='global coolness!')
# @arguments
# class CleanArguments:
#     ...
# @arguments
# class ConsoleArguments:
#     root: int
#     command: Arguments = command(
#         build=BuildArguments,
#         clean=CleanArguments,
#         extra={
#             'your-mom': BuildArguments
#         }
#     )
# print(ConsoleArguments.parse_args([
#     '69', 'build', 'proj1', 'plcl', '--root', 'my-root', '-h'
# ]))