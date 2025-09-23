from __future__ import annotations

"""Public package interface for ``pyars``."""

from pathlib import Path

from .container import arguments, ArgumentContainer as Arguments, InvalidArgumentsError
from .argument import (
    CommandArgument as command,
    PositionalArgument as positional,
    OptionArgument as option,
    FlagArgument as flag,
)

__all__ = [
    'arguments',
    'command',
    'positional',
    'option',
    'flag',
    'Arguments',
    'InvalidArgumentsError',
    'Path',
]
