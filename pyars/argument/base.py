from __future__ import annotations

"""Base definitions shared by all argument types."""

from argparse import ArgumentParser, Namespace
from typing import Callable

from attrs import Attribute


class ArgumentType:
    """Base interface that defines parsing behaviour for a single attribute."""

    @staticmethod
    def to_console_name(name: str) -> str:
        """Convert an attribute name into a CLI-friendly option name."""
        return name.replace('_', '-')

    def get_converter(self, attr: Attribute) -> type | Callable | None:
        """Return a callable that converts an argument value early during parsing."""
        return None

    def get_late_converter(self, attr: Attribute) -> type | Callable | None:
        """Return a callable that converts an argument value after parsing."""
        return None

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        """Add the CLI option for ``attr`` to ``parser``."""
        raise NotImplementedError

    def extract(self, prefix: str, attr: Attribute, namespace: Namespace):
        """Extract a value for ``attr`` from ``namespace``."""
        raise NotImplementedError
