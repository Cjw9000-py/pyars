from __future__ import annotations

"""Public package interface for ``pyars``."""

from pathlib import Path

from .container import arguments, ArgumentContainer as Arguments, InvalidArgumentsError
from .argument_types import (
    CommandArgument as command,
    PositionalArgument as positional,
    FlagArgument as flag,
    SwitchArgument as switch,
)

__all__ = [
    'arguments',
    'command',
    'positional',
    'flag',
    'switch',
    'Arguments',
    'InvalidArgumentsError',
    'Path',
]
