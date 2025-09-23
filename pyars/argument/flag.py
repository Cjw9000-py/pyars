from __future__ import annotations

"""Boolean flag arguments."""

from attrs import Attribute

from .base import ArgumentType


class FlagArgument(ArgumentType):
    """A toggle-style flag that stores ``True`` when present."""

    def __init__(
        self,
        *names: str,
        default: bool = False,
        help: str | None = None,
    ) -> None:
        self.names = names
        self.default = bool(default)
        self.help = help

    def _option_names(self, attr: Attribute) -> list[str]:
        names = list(self.names)
        long_name = f"--{self.to_console_name(attr.name)}"
        if not names:
            names.append(long_name)
        else:
            if all(not name.startswith('--') for name in names):
                names.append(long_name)
        return names

    def add_argument(self, prefix: str, attr: Attribute, parser):
        parser.add_argument(
            *self._option_names(attr),
            dest=prefix + attr.name,
            action='store_true',
            default=self.default,
            help=self.help,
        )

    def extract(self, prefix: str, attr: Attribute, namespace):
        return bool(getattr(namespace, prefix + attr.name))


__all__ = ['FlagArgument']
