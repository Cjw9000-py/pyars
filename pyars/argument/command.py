from __future__ import annotations

"""Sub-command argument type selecting another :class:`ArgumentContainer`."""

from argparse import ArgumentParser, Namespace
from typing import TYPE_CHECKING

from attrs import Attribute

from .base import ArgumentType

if TYPE_CHECKING:  # pragma: no cover - import cycle guard
    from ..container import ArgumentContainer


def _validate_container_type(value: type) -> None:
    """Assert ``value`` behaves like an ``ArgumentContainer`` subclass."""
    if __debug__:
        from ..container import ArgumentContainer

        msg = (
            "value is not an ArgumentContainer subclass (define with @arguments): "
            f"{value}"
        )
        assert isinstance(value, type), msg
        assert issubclass(value, ArgumentContainer), msg


class CommandArgument(ArgumentType):
    """Represents a sub-command argument selecting another :class:`ArgumentContainer`."""

    def __init__(
        self,
        extra: dict[str, type['ArgumentContainer']] | None = None,
        **kwargs: type['ArgumentContainer'],
    ):
        """Create a command argument."""
        extra = {} if extra is None else extra
        if isinstance(extra, type):
            raise TypeError(
                "extra is not allowed as a command name, it should be a dict with "
                "non python keyword argument names. if you want to use it define "
                "it like this extra={'extra':%s }" % extra
            )

        for key, value in kwargs.items():
            _validate_container_type(value)

        assert isinstance(extra, dict)
        extra.update(kwargs)
        self.options: dict[str, type['ArgumentContainer']] = extra.copy()

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        """Register sub-parsers for each possible command option."""
        subparsers = parser.add_subparsers(dest=prefix + attr.name)
        subparsers.required = True  # ensure missing commands raise an error
        for name, option in self.options.items():
            subparser = subparsers.add_parser(name)
            option.add_arguments(f"{prefix}{attr.name}-", subparser)

    def extract(self, prefix: str, attr: Attribute, namespace: Namespace):
        """Instantiate the selected command container from ``namespace``."""
        key = getattr(namespace, prefix + attr.name)
        if key is None:
            from ..container import InvalidArgumentsError

            raise InvalidArgumentsError(
                f"{attr.name}: command selection is required"
            )
        option = self.options[key]
        return option.from_namespace(f"{prefix}{attr.name}-", namespace)


__all__ = ["CommandArgument"]
