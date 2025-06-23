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
