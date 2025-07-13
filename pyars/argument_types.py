from __future__ import annotations

from pathlib import Path
from types import GenericAlias, UnionType
from typing import Callable
from argparse import ArgumentParser, Namespace
from attrs import Attribute, NOTHING

from .container import ArgumentContainer


class ArgumentType:
    """Base interface for argument behaviour."""

    @staticmethod
    def to_console_name(name: str) -> str:
        return name.replace('_', '-')

    def get_converter(self, attr: Attribute) -> type | Callable | None:
        return None

    def get_late_converter(self, attr: Attribute) -> type | Callable | None:
        return None

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        raise NotImplementedError

    def extract(self, prefix: str, attr: Attribute, namespace: Namespace):
        raise NotImplementedError


class CommandArgument(ArgumentType):
    def __init__(self, extra: dict[str, type[ArgumentContainer]] | None = None, **kwargs: type[ArgumentContainer]):
        extra = {} if extra is None else extra
        if isinstance(extra, type):
            raise TypeError(
                "extra is not allowed as a command name, "
                "it should be a dict with non python keyword argument names. "
                "if you want to use it define it like this extra={'extra':%s }" % extra
            )

        for key, value in kwargs.items():
            if __debug__:
                msg = (
                    f"value for kwarg {key} is not of instance ArgumentContainer "
                    f"(ie. not defined with @arguments): {value}"
                )
                assert isinstance(value, type), msg
                assert issubclass(value, ArgumentContainer), msg

        assert isinstance(extra, dict)
        extra.update(kwargs)
        self.options: dict[str, type[ArgumentContainer]] = extra.copy()

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        subparsers = parser.add_subparsers(dest=prefix + attr.name)
        for name, option in self.options.items():
            subparser = subparsers.add_parser(name)
            option.add_arguments(f"{prefix}{attr.name}-", subparser)

    def extract(self, prefix: str, attr: Attribute, namespace: Namespace):
        option = self.options[getattr(namespace, prefix + attr.name)]
        return option.from_namespace(f"{prefix}{attr.name}-", namespace)


class ValueArgument(ArgumentType):
    def __init__(self, nargs: str | None = None, type: type | Callable | None = None, help: str | None = None):  # noqa
        self.nargs = nargs
        self.type = type
        self.help = help

    def guess_converter(self, s: str) -> type | Callable | None:
        keywords = {
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'tuple': tuple,
            'set': set,
            'frozenset': frozenset,
            'bytes': bytes,
            'bytearray': bytearray,
            'str': str,
            'Path': Path,
        }
        for keyword, conv in keywords.items():
            if s.startswith(keyword):
                return conv
        return None

    def get_converter(self, attr: Attribute) -> type | Callable | None:
        type_value = None
        if self.type is not None:
            type_value = self.type
        elif not isinstance(attr.type, str):
            type_value = attr.type
        else:
            try:
                type_value = eval(attr.type, globals())
            except Exception:
                type_value = self.guess_converter(attr.type)

        if isinstance(type_value, GenericAlias):
            type_value = type_value.__origin__
        if isinstance(type_value, UnionType):
            return None
        assert callable(type_value) or type_value is None, f"Type converter {type_value} is not callable or a type"
        return type_value

    def get_late_converter(self, attr: Attribute) -> type | Callable | None:
        return None

    def get_args(self, attr: Attribute) -> list[object]:
        return []

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, object]:
        kwargs = {'dest': prefix + attr.name}
        if self.nargs is not None:
            kwargs['nargs'] = self.nargs
        converter = self.get_converter(attr)
        if converter is not None:
            kwargs['type'] = converter
        if self.help is not None:
            kwargs['help'] = self.help
        return kwargs

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        parser.add_argument(*self.get_args(attr), **self.get_kwargs(prefix, attr))

    def extract(self, prefix: str, attr: Attribute, namespace: Namespace):
        conv = self.get_late_converter(attr)
        if conv is None:
            conv = lambda x: x
        return conv(getattr(namespace, prefix + attr.name))


class PositionalArgument(ValueArgument):
    def get_converter(self, attr: Attribute) -> type | Callable | None:
        conv = super().get_converter(attr)
        if not hasattr(conv, '__iter__'):
            return conv
        return None

    def get_late_converter(self, attr: Attribute) -> type | Callable | None:
        conv = super().get_converter(attr)
        if hasattr(conv, '__iter__'):
            return conv
        return None

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, object]:
        kwargs = super().get_kwargs(prefix, attr)
        kwargs['metavar'] = attr.name
        return kwargs


class FlagArgument(ValueArgument):
    def __init__(self, *opts: str, nargs: str | None = None, type: type | Callable | None = None, default: object = NOTHING, extra_opts: list[str] | set[str] | tuple[str] | str | None = None, help: str | None = None):  # noqa
        super().__init__(nargs=nargs, type=type, help=help)
        self.default = default
        self.opts = opts
        if extra_opts is not None:
            self.extra_opts = set(extra_opts) if not isinstance(extra_opts, str) else {extra_opts}
        else:
            self.extra_opts = None

    def get_console_names(self, attr: Attribute) -> set[str]:
        names: set[str] = set()
        if self.opts:
            names.update(self.opts)
        else:
            names.add(self.to_console_name(attr.name))
        if self.extra_opts:
            names.update(self.extra_opts)
        formatted = {f"--{name}" for name in names if not name.startswith('-')}
        return formatted

    def get_args(self, attr: Attribute) -> list[object]:
        args = super().get_args(attr)
        args.extend(self.get_console_names(attr))
        return args

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, object]:
        kwargs = super().get_kwargs(prefix, attr)
        if self.default is not NOTHING:
            kwargs['default'] = self.default
            kwargs['required'] = False
        else:
            kwargs['required'] = True
        return kwargs


class SwitchArgument(ValueArgument):
    def __init__(self, name: str | None = None, enable: bool = True, disable: bool = True, default: bool = False, help_suffix: str | None = None, help: str | None = None):  # noqa
        super().__init__(help=help)
        self.name = name
        self.enable = enable
        self.disable = disable
        self.default = default
        self.help_suffix = help_suffix

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        name = self.name if self.name is not None else self.to_console_name(attr.name)
        dest = f"{prefix}{attr.name}"
        if self.enable:
            parser.add_argument(
                f"--{name}",
                dest=dest,
                action='store_true',
                default=self.default,
                help=self.help if self.help else f"Enable {self.help_suffix}",
            )
        if self.disable:
            parser.add_argument(
                f"--no-{name}",
                dest=dest,
                action='store_false',
                default=self.default,
                help=self.help if self.help else f"Disable {self.help_suffix}",
            )
