from __future__ import annotations

from pathlib import Path

from .container import arguments, ArgumentContainer as Arguments
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
    'Path',
]
