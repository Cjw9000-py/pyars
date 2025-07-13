from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Iterable, Self, Callable

from attrs import define, fields, Attribute, NOTHING


class ArgumentContainer:
    @classmethod
    def new_parser(cls, *args, **kwargs) -> ArgumentParser:
        parser = ArgumentParser(*args, **kwargs)
        cls.add_arguments('', parser)
        return parser

    @classmethod
    def get_arguments(cls) -> Iterable[tuple[Attribute, "ArgumentType"]]:
        from .argument_types import ArgumentType, PositionalArgument
        for field in fields(cls):
            argument = field.default
            if field.default in (NOTHING, None, ...):
                argument = PositionalArgument()
            if not isinstance(argument, ArgumentType):
                raise TypeError(f'Use a argument type as a default value, not {argument}')
            yield field, argument

    @classmethod
    def add_arguments(cls, prefix: str, parser: ArgumentParser):
        for field, argument in cls.get_arguments():
            argument.add_argument(prefix, field, parser)

    @classmethod
    def namespace_to_dict(cls, prefix: str, namespace: Namespace) -> dict[str, object]:
        kwargs: dict[str, object] = {}
        for field, argument in cls.get_arguments():
            kwargs[field.name] = argument.extract(prefix, field, namespace)
        return kwargs

    @classmethod
    def from_namespace(cls, prefix: str, namespace: Namespace) -> Self:
        return cls(**cls.namespace_to_dict(prefix, namespace))

    @classmethod
    def parse_args(cls, argv: list[str] | None = None) -> Self:
        parser = cls.new_parser()
        namespace = parser.parse_args(argv)
        instance = cls.from_namespace('', namespace)
        return instance


def arguments(outer_cls: type | None = None, **kwargs) -> type[ArgumentContainer] | Callable:
    def wrapper(cls: type) -> type[ArgumentContainer]:
        cls = define(**kwargs)(cls)
        mixed_type: type[ArgumentContainer] = type(cls.__name__, (cls, ArgumentContainer), {})
        return mixed_type

    if outer_cls is None:
        return wrapper
    return wrapper(outer_cls)
