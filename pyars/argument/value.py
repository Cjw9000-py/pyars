from __future__ import annotations

"""Shared logic for argument types that carry values."""

from argparse import ArgumentParser, Namespace
from collections.abc import Iterable as IterableABC
from pathlib import Path
from types import GenericAlias, SimpleNamespace, UnionType
from typing import Callable, get_type_hints, Any

from attrs import Attribute, NOTHING

from .base import ArgumentType

_ALLOWED_NAMES: dict[str, type[Any]] = {
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

_COLLECTION_TYPES = {list, set, tuple}


def _resolve_annotation(annotation: str) -> Any | None:
    """Return a type object for ``annotation`` if allowed."""
    if annotation in _ALLOWED_NAMES:
        return _ALLOWED_NAMES[annotation]
    try:
        dummy = SimpleNamespace()
        dummy.__annotations__ = {'v': annotation}
        return get_type_hints(dummy, globalns=_ALLOWED_NAMES)['v']
    except Exception:
        return None


def _get_origin(annotation: Any) -> Any | None:
    return getattr(annotation, '__origin__', None)


def _get_args(annotation: Any) -> tuple[Any, ...]:
    return getattr(annotation, '__args__', ())


class ValueArgument(ArgumentType):
    """Argument that holds one or more primitive values."""

    def __init__(
        self,
        *,
        nargs: str | None = None,
        convert: Callable[[Any], Any] | None = None,
        default: Any = NOTHING,
        help: str | None = None,
    ) -> None:
        self.nargs = nargs
        self.convert = convert
        self.default = default
        self.help = help

    # --- configuration helpers -------------------------------------------------

    def _resolve_type(self, attr: Attribute) -> Any | None:
        annotation = attr.type
        if isinstance(annotation, str):
            return _resolve_annotation(annotation)
        if isinstance(annotation, GenericAlias):
            return annotation
        if isinstance(annotation, UnionType):
            return annotation
        return annotation

    def _collection_factory(self, resolved: Any | None) -> Callable[[IterableABC[Any]], Any] | None:
        origin = _get_origin(resolved)
        if origin in _COLLECTION_TYPES:
            return origin
        if resolved in _COLLECTION_TYPES:
            return resolved
        return None

    def _element_type(self, resolved: Any | None) -> Any | None:
        origin = _get_origin(resolved)
        if origin in _COLLECTION_TYPES:
            args = _get_args(resolved)
            return args[0] if args else None
        return resolved

    def _element_converter(self, attr: Attribute) -> Callable[[Any], Any] | None:
        if self.convert is not None:
            return self.convert
        resolved = self._resolve_type(attr)
        element = self._element_type(resolved)
        if element is None or element is Any:
            return None
        if isinstance(element, UnionType):
            return None
        if isinstance(element, GenericAlias):
            element = _get_origin(element)
        if isinstance(element, type) or callable(element):
            return element
        return None

    def _apply_element_converter(self, value: Any, converter: Callable[[Any], Any] | None) -> Any:
        if converter is None:
            return value
        try:
            return converter(value)
        except Exception as exc:  # pragma: no cover - conversion errors bubble up
            raise ValueError(f'Failed to convert argument value {value!r}') from exc

    def _coerce_collection(
        self,
        attr: Attribute,
        value: Any,
        *,
        converter: Callable[[Any], Any] | None,
    ) -> Any:
        resolved = self._resolve_type(attr)
        factory = self._collection_factory(resolved)
        if factory is None:
            return self._apply_element_converter(value, converter)

        if value is None:
            items: list[Any] = []
        elif isinstance(value, factory):
            items = list(value)
        elif isinstance(value, (list, tuple, set)):
            items = list(value)
        else:
            items = [value]

        converted = [self._apply_element_converter(item, converter) for item in items]

        if factory is list:
            return converted
        if factory is set:
            return set(converted)
        if factory is tuple:
            return tuple(converted)
        return converted

    # --- argparse integration --------------------------------------------------

    def destination(self, prefix: str, attr: Attribute) -> str | None:
        """Return the argparse destination name, or ``None`` for positional args."""
        return f"{prefix}{attr.name}"

    def get_args(self, attr: Attribute) -> list[str]:
        return []

    def get_kwargs(self, prefix: str, attr: Attribute) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        dest = self.destination(prefix, attr)
        if dest is not None:
            kwargs['dest'] = dest
        if self.nargs is not None:
            kwargs['nargs'] = self.nargs
        converter = self._element_converter(attr)
        if converter is not None:
            kwargs['type'] = converter
        if self.help is not None:
            kwargs['help'] = self.help
        default = self.get_default(attr)
        if default is not NOTHING:
            kwargs['default'] = default
        return kwargs

    def get_default(self, attr: Attribute) -> Any:
        if self.default is NOTHING:
            return NOTHING
        converter = self._element_converter(attr)
        return self._coerce_collection(attr, self.default, converter=converter)

    def add_argument(self, prefix: str, attr: Attribute, parser: ArgumentParser):
        parser.add_argument(*self.get_args(attr), **self.get_kwargs(prefix, attr))

    def extract(self, prefix: str, attr: Attribute, namespace: Namespace):
        converter = self._element_converter(attr)
        key = self.destination(prefix, attr) or attr.name
        if not hasattr(namespace, key):
            key = attr.name
        raw_value = getattr(namespace, key)
        return self._coerce_collection(attr, raw_value, converter=converter)


__all__ = ['ValueArgument']
