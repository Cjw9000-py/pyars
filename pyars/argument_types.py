from __future__ import annotations

"""Argument types used by :class:`pyars.ArgumentContainer`.

This module contains small classes that describe how the command line should
be parsed and mapped onto attrs based classes.  Each argument type exposes
methods for extending :class:`argparse.ArgumentParser` and for extracting
values from a parsed :class:`argparse.Namespace`.
"""

from pathlib import Path
from types import GenericAlias, UnionType
from typing import Callable
from argparse import ArgumentParser, Namespace
from enum import Enum
from distutils.util import strtobool
import os
from attrs import Attribute, NOTHING

from .container import ArgumentContainer


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


class CommandArgument(ArgumentType):
    """Represents a sub-command argument selecting another :class:`ArgumentContainer`."""

    def __init__(self, extra: dict[str, type[ArgumentContainer]] | None = None, **kwargs: type[ArgumentContainer]):
        """Create a command argument.

        Parameters
        ----------
        extra:
            Additional mapping of command name to container type.
        **kwargs:
            Each keyword defines a command name mapped to an ``ArgumentContainer`` subclass.
        """

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
        """Register sub-parsers for each possible command option."""
        subparsers = parser.add_subparsers(dest=prefix + attr.name)
        for name, option in self.options.items():
            subparser = subparsers.add_parser(name)
            option.add_arguments(f"{prefix}{attr.name}-", subparser)

    def extract(self, prefix: str, attr: Attribute, namespace: Namespace):
        """Instantiate the selected command container from ``namespace``."""
        option = self.options[getattr(namespace, prefix + attr.name)]
        return option.from_namespace(f"{prefix}{attr.name}-", namespace)


class ValueArgument(ArgumentType):
    """Argument that holds one or more primitive values."""

    def __init__(
        self,
        nargs: str | None = None,
        type: type | Callable | None = None,
        *,
        env_var: str | None = None,
        help: str | None = None,
    ) -> None:  # noqa: D401
        """Create a value argument."""
        self.nargs = nargs
        self.type = type
        self.help = help
        self.env_var = env_var

    def get_env_default(self, attr: Attribute):
        if self.env_var is None:
            return NOTHING
        raw = os.getenv(self.env_var)
        if raw is None:
            return NOTHING
        conv = self.get_converter(attr)
        if conv is None:
            return raw
        try:
            return conv(raw)
        except Exception as exc:  # pragma: no cover - unlikely
            raise ValueError(
                f"Invalid value for environment variable {self.env_var}: {raw}"
            ) from exc

    def resolve_default(self, attr: Attribute, fallback: object = NOTHING) -> object:
        env_default = self.get_env_default(attr)
        if env_default is not NOTHING:
            return env_default
        return fallback

    def guess_converter(self, s: str) -> type | Callable | None:
        """Best-effort guess for a converter based on a string annotation."""
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
        """Resolve the converter used during parsing."""
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
        """Converter applied after parsing; defaults to ``None``."""
        return None

    def get_args(self, attr: Attribute) -> list[object]:
        """Positional arguments for :func:`argparse.ArgumentParser.add_argument`."""
        return []

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, object]:
        """Keyword arguments for :func:`argparse.ArgumentParser.add_argument`."""
        kwargs = {'dest': prefix + attr.name}
        if self.nargs is not None:
            kwargs['nargs'] = self.nargs
        converter = self.get_converter(attr)
        if converter is not None:
            kwargs['type'] = converter
        if self.help is not None:
            kwargs['help'] = self.help
        env_default = self.get_env_default(attr)
        if env_default is not NOTHING:
            kwargs['default'] = env_default
        return kwargs

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        """Register a standard ``argparse`` option."""
        parser.add_argument(*self.get_args(attr), **self.get_kwargs(prefix, attr))

    def extract(self, prefix: str, attr: Attribute, namespace: Namespace):
        """Extract and optionally convert the parsed value."""
        conv = self.get_late_converter(attr)
        if conv is None:
            conv = lambda x: x
        return conv(getattr(namespace, prefix + attr.name))


class PositionalArgument(ValueArgument):
    """A value argument that is provided without a leading flag."""

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
    """Named command line flag that yields a value."""

    def __init__(
        self,
        *opts: str,
        nargs: str | None = None,
        type: type | Callable | None = None,
        default: object = NOTHING,
        extra_opts: list[str] | set[str] | tuple[str] | str | None = None,
        env_var: str | None = None,
        help: str | None = None,
    ):  # noqa: D401
        """Create a flag argument."""
        super().__init__(nargs=nargs, type=type, env_var=env_var, help=help)
        self.default = default
        self.opts = opts
        if extra_opts is not None:
            self.extra_opts = set(extra_opts) if not isinstance(extra_opts, str) else {extra_opts}
        else:
            self.extra_opts = None

    def get_console_names(self, attr: Attribute) -> set[str]:
        """Return all console option names for ``attr``."""
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
        """Include console option names alongside normal args."""
        args = super().get_args(attr)
        args.extend(self.get_console_names(attr))
        return args

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, object]:
        """Keyword arguments including default handling."""
        kwargs = super().get_kwargs(prefix, attr)
        if self.default is not NOTHING:
            kwargs['default'] = self.default
            kwargs['required'] = False
        elif 'default' in kwargs:
            kwargs['required'] = False
        else:
            kwargs['required'] = True
        return kwargs


class SwitchArgument(ValueArgument):
    """Boolean flag that supports ``--feature``/``--no-feature`` style switches."""

    def __init__(
        self,
        name: str | None = None,
        enable: bool = True,
        disable: bool = True,
        default: bool = False,
        *,
        env_var: str | None = None,
        help_suffix: str | None = None,
        help: str | None = None,
    ) -> None:  # noqa: D401
        """Create a switch argument."""
        super().__init__(env_var=env_var, help=help)
        self.name = name
        self.enable = enable
        self.disable = disable
        self.default = default
        self.help_suffix = help_suffix

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        """Register ``--flag`` and/or ``--no-flag`` options."""
        name = self.name if self.name is not None else self.to_console_name(attr.name)
        dest = f"{prefix}{attr.name}"
        default = self.resolve_default(attr, self.default)
        if self.enable:
            parser.add_argument(
                f"--{name}",
                dest=dest,
                action='store_true',
                default=default,
                help=self.help if self.help else f"Enable {self.help_suffix}",
            )
        if self.disable:
            parser.add_argument(
                f"--no-{name}",
                dest=dest,
                action='store_false',
                default=default,
                help=self.help if self.help else f"Disable {self.help_suffix}",
            )


class EnumArgument(FlagArgument):
    """Flag that accepts only values from a specific :class:`Enum`."""

    def __init__(
        self,
        enum: type[Enum],
        *opts: str,
        default: Enum | object = NOTHING,
        extra_opts: list[str] | set[str] | tuple[str] | str | None = None,
        env_var: str | None = None,
        help: str | None = None,
    ) -> None:
        self.enum = enum
        super().__init__(*opts, default=default, extra_opts=extra_opts, env_var=env_var, help=help)

    def get_converter(self, attr: Attribute):
        def convert(value: str | Enum) -> Enum:
            if isinstance(value, self.enum):
                return value
            try:
                return self.enum[value]
            except KeyError:
                try:
                    return self.enum(value)
                except Exception as exc:
                    allowed = ', '.join(m.name for m in self.enum)
                    raise ValueError(f"Expected one of {allowed}, got {value}") from exc

        return convert

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, object]:
        kwargs = super().get_kwargs(prefix, attr)
        kwargs['choices'] = list(self.enum)
        return kwargs


class ListArgument(FlagArgument):
    """Flag accepting a delimiter-separated sequence."""

    def __init__(
        self,
        *opts: str,
        delimiter: str = ',',
        item_type: Callable | type | None = str,
        container: type[list] | type[set] = list,
        default: object = NOTHING,
        extra_opts: list[str] | set[str] | tuple[str] | str | None = None,
        env_var: str | None = None,
        help: str | None = None,
    ) -> None:
        super().__init__(*opts, type=None, default=default, extra_opts=extra_opts, env_var=env_var, help=help)
        self.delimiter = delimiter
        self.item_type = item_type
        self.container = container

    def get_converter(self, attr: Attribute):
        def convert(value: str) -> object:
            items = [] if value == '' else value.split(self.delimiter)
            conv = self.item_type
            if conv:
                items = [conv(v) for v in items]
            return self.container(items)

        return convert
