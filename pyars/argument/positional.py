from __future__ import annotations

"""Positional argument type implementation."""

from typing import Any, Callable

from attrs import Attribute, NOTHING

from .value import ValueArgument


class PositionalArgument(ValueArgument):
    """A value argument that is provided without a leading flag."""

    def __init__(
        self,
        *,
        nargs: str | None = None,
        convert: Callable[[Any], Any] | None = None,
        default: Any = NOTHING,
        help: str | None = None,
    ) -> None:
        super().__init__(nargs=nargs, convert=convert, default=default, help=help)

    def destination(self, prefix: str, attr: Attribute) -> str | None:  # noqa: D401 - documented in base class
        return None

    def get_args(self, attr: Attribute) -> list[str]:
        return [attr.name]

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, Any]:
        kwargs = super().get_kwargs(prefix, attr)
        kwargs['metavar'] = attr.name.upper()
        return kwargs


__all__ = ['PositionalArgument']
