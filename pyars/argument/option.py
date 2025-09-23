from __future__ import annotations

"""Option arguments that accept explicit values via named flags."""

from typing import Any, Callable

from attrs import Attribute, NOTHING

from .value import ValueArgument


class OptionArgument(ValueArgument):
    """A named option that consumes a value from the command line."""

    def __init__(
        self,
        *names: str,
        nargs: str | None = None,
        convert: Callable[[Any], Any] | None = None,
        default: Any = NOTHING,
        help: str | None = None,
        required: bool | None = None,
    ) -> None:
        super().__init__(nargs=nargs, convert=convert, default=default, help=help)
        self.names = names
        self.required = required

    def _option_names(self, attr: Attribute) -> tuple[str, ...]:
        if self.names:
            return tuple(self.names)
        return (f"--{self.to_console_name(attr.name)}",)

    def _auto_long_option(self, attr: Attribute) -> str:
        return f"--{self.to_console_name(attr.name)}"

    def get_args(self, attr: Attribute) -> list[str]:
        names = list(self._option_names(attr))
        if not names:
            names.append(self._auto_long_option(attr))
        else:
            long_name = self._auto_long_option(attr)
            if all(not name.startswith('--') for name in names):
                names.append(long_name)
        return names

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, Any]:
        kwargs = super().get_kwargs(prefix, attr)
        if self.required is not None:
            kwargs['required'] = self.required
        else:
            kwargs['required'] = self.default is NOTHING
        return kwargs


__all__ = ['OptionArgument']
