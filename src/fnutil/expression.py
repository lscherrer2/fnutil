from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, SupportsAbs

from fnutil._protocols import (
    SupportsAdd,
    SupportsFloordiv,
    SupportsGe,
    SupportsGt,
    SupportsLe,
    SupportsLt,
    SupportsMod,
    SupportsMul,
    SupportsNeg,
    SupportsPow,
    SupportsSub,
    SupportsTruediv,
)

if TYPE_CHECKING:
    from fnutil.iterator import Iterator


class Expression[T]:
    def __init__(self, value: T) -> None:
        self._inner = value

    @property
    def value(self) -> T:
        return self._inner

    def __repr__(self) -> str:
        return f"Expression({self._inner!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Expression):
            return self._inner == other._inner  # type: ignore[operator]
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._inner)

    def map[U](self, fn: Callable[[T], U]) -> Expression[U]:
        """Apply *fn* to the inner value and wrap the result."""
        return Expression(fn(self._inner))

    def flat_map[U](self, fn: Callable[[T], Expression[U]]) -> Expression[U]:
        """Apply *fn* and unwrap one level of Expression."""
        return fn(self._inner)

    def pipe(self, *fns: Callable) -> Expression:
        """Thread the value through a sequence of functions left-to-right."""
        result: object = self._inner
        for fn in fns:
            result = fn(result)
        return Expression(result)

    def then[U](self, fn: Callable[[T], U]) -> U:
        """Apply *fn* to the inner value and return the raw result (no wrap)."""
        return fn(self._inner)

    def inspect(self, fn: Callable[[T], object]) -> Expression[T]:
        """Call *fn* with the inner value for side-effects; return self."""
        fn(self._inner)
        return self

    @property
    def is_some(self) -> bool:
        """True when the inner value is not None."""
        return self._inner is not None

    @property
    def is_none(self) -> bool:
        """True when the inner value is None."""
        return self._inner is None

    def filter[U](self, fn: Callable[[T], bool]) -> Expression[T | None]:
        """Return self if *fn(value)* is truthy, else Expression(None)."""
        if fn(self._inner):
            return Expression(self._inner)
        return Expression(None)

    def or_else[U](self, default: U) -> Expression[T | U]:
        """Return self when is_some, else Expression(default)."""
        if self._inner is not None:
            return Expression(self._inner)
        return Expression(default)

    def or_else_with[U](self, fn: Callable[[], U]) -> Expression[T | U]:
        """Return self when is_some, else Expression(fn())."""
        if self._inner is not None:
            return Expression(self._inner)
        return Expression(fn())

    def unwrap_or[U](self, default: U) -> T | U:
        """Return the inner value when is_some, else *default*."""
        if self._inner is not None:
            return self._inner
        return default

    def iter[U](self: Expression[Iterable[U]]) -> Iterator[U]:
        from fnutil.iterator import it

        return it(self._inner)

    def __add__[S: SupportsAdd](
        self: Expression[S], other: Expression[S]
    ) -> Expression[S]:
        return Expression(self._inner + other._inner)  # type: ignore[operator]

    def __sub__[S: SupportsSub](
        self: Expression[S], other: Expression[S]
    ) -> Expression[S]:
        return Expression(self._inner - other._inner)  # type: ignore[operator]

    def __mul__[S: SupportsMul](
        self: Expression[S], other: Expression[S]
    ) -> Expression[S]:
        return Expression(self._inner * other._inner)  # type: ignore[operator]

    def __truediv__[S: SupportsTruediv](
        self: Expression[S], other: Expression[S]
    ) -> Expression[S]:
        return Expression(self._inner / other._inner)  # type: ignore[operator]

    def __floordiv__[S: SupportsFloordiv](
        self: Expression[S], other: Expression[S]
    ) -> Expression[S]:
        return Expression(self._inner // other._inner)  # type: ignore[operator]

    def __mod__[S: SupportsMod](
        self: Expression[S], other: Expression[S]
    ) -> Expression[S]:
        return Expression(self._inner % other._inner)  # type: ignore[operator]

    def __pow__[S: SupportsPow](
        self: Expression[S], other: Expression[S]
    ) -> Expression[S]:
        return Expression(self._inner**other._inner)  # type: ignore[operator]

    def __neg__[S: SupportsNeg](self: Expression[S]) -> Expression[S]:
        return Expression(-self._inner)  # type: ignore[operator]

    def __abs__[S: SupportsAbs](self: Expression[S]) -> Expression[S]:
        return Expression(abs(self._inner))  # type: ignore[arg-type]

    def __lt__[S: SupportsLt](
        self: Expression[S], other: Expression[S]
    ) -> bool:
        return self._inner < other._inner  # type: ignore[operator]

    def __le__[S: SupportsLe](
        self: Expression[S], other: Expression[S]
    ) -> bool:
        return self._inner <= other._inner  # type: ignore[operator]

    def __gt__[S: SupportsGt](
        self: Expression[S], other: Expression[S]
    ) -> bool:
        return self._inner > other._inner  # type: ignore[operator]

    def __ge__[S: SupportsGe](
        self: Expression[S], other: Expression[S]
    ) -> bool:
        return self._inner >= other._inner  # type: ignore[operator]


def expr[T](value: T) -> Expression[T]:
    """Wrap *value* in an Expression."""
    return Expression(value=value)
