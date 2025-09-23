from __future__ import annotations

"""Utilities for describing command line arguments using attrs classes."""

from argparse import ArgumentParser, Namespace
from typing import Iterable, Callable, TypeVar
import sys

from attrs import define, fields, Attribute, NOTHING

from .argument import (
    ArgumentType,
    PositionalArgument,
    CommandArgument,
)

T = TypeVar('T', bound='ArgumentContainer')


class InvalidArgumentsError(Exception):
    """Raised when incompatible command line options are detected."""


class ArgumentContainer:
    """Mix-in providing ``argparse`` integration for attrs classes."""

    @classmethod
    def new_parser(
        cls,
        *args,
        callbacks: Callable[[ArgumentParser], None]
        | Iterable[Callable[[ArgumentParser], None]]
        | None = None,
        **kwargs,
    ) -> ArgumentParser:
        """Return an ``ArgumentParser`` pre-configured for ``cls``."""
        parser = ArgumentParser(*args, **kwargs)
        cls.add_arguments('', parser)

        if callbacks is not None:
            if callable(callbacks):
                callbacks = (callbacks,)
            for cb in callbacks:
                cb(parser)

        return parser

    @classmethod
    def get_arguments(cls) -> Iterable[tuple[Attribute, ArgumentType]]:
        """Yield ``(field, argument_type)`` tuples for all attrs fields."""
        for field in fields(cls):
            argument = field.default
            if field.default is NOTHING or field.default is ...:
                argument = PositionalArgument()
            if not isinstance(argument, ArgumentType):
                raise TypeError(
                    f'Use an argument type as a default value, not {argument!r}'
                )
            yield field, argument

    @classmethod
    def add_arguments(cls, prefix: str, parser: ArgumentParser):
        """Add options for all fields of ``cls`` to ``parser``."""
        for field, argument in cls.get_arguments():
            argument.add_argument(prefix, field, parser)

    @classmethod
    def namespace_to_dict(cls, prefix: str, namespace: Namespace) -> dict[str, object]:
        """Create a kwargs dict from ``namespace`` for constructing ``cls``."""
        kwargs: dict[str, object] = {}
        for field, argument in cls.get_arguments():
            kwargs[field.name] = argument.extract(prefix, field, namespace)
        return kwargs

    @classmethod
    def pre_validate(cls, argv: list[str]) -> None:
        """Validate ``argv`` before parsing and raise ``InvalidArgumentsError`` on conflicts."""
        for field, argument in cls.get_arguments():
            if isinstance(argument, CommandArgument):
                for cmd_name, container_cls in argument.options.items():
                    if cmd_name in argv:
                        idx = argv.index(cmd_name)
                        container_cls.pre_validate(argv[idx + 1 :])
                        break

    @classmethod
    def from_namespace(cls: type[T], prefix: str, namespace: Namespace) -> T:
        """Instantiate ``cls`` using values extracted from ``namespace``."""
        return cls(**cls.namespace_to_dict(prefix, namespace))

    @classmethod
    def parse_args(cls: type[T], argv: list[str] | None = None) -> T:
        """Parse ``argv`` and return an instance of ``cls``."""
        parser = cls.new_parser()
        raw = sys.argv[1:] if argv is None else argv
        cls.pre_validate(list(raw))
        namespace = parser.parse_args(argv)
        return cls.from_namespace('', namespace)


def arguments(outer_cls: type | None = None, **kwargs) -> type[ArgumentContainer] | Callable:
    """Decorate a class to become an ``ArgumentContainer``."""

    def wrapper(cls: type) -> type[ArgumentContainer]:
        cls = define(**kwargs)(cls)
        mixed_type: type[ArgumentContainer] = type(
            cls.__name__,
            (cls, ArgumentContainer),
            {'__module__': cls.__module__},
        )
        return mixed_type

    if outer_cls is None:
        return wrapper
    return wrapper(outer_cls)
