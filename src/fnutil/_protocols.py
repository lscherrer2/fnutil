from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsAdd[T](Protocol):
    def __add__(self, other: T) -> T: ...


@runtime_checkable
class SupportsSub[T](Protocol):
    def __sub__(self, other: T) -> T: ...


@runtime_checkable
class SupportsMul[T](Protocol):
    def __mul__(self, other: T) -> T: ...


@runtime_checkable
class SupportsTruediv[T](Protocol):
    def __truediv__(self, other: T) -> T: ...


@runtime_checkable
class SupportsFloordiv[T](Protocol):
    def __floordiv__(self, other: T) -> T: ...


@runtime_checkable
class SupportsMod[T](Protocol):
    def __mod__(self, other: T) -> T: ...


@runtime_checkable
class SupportsPow[T](Protocol):
    def __pow__(self, other: T) -> T: ...


@runtime_checkable
class SupportsNeg[T](Protocol):
    def __neg__(self) -> T: ...


@runtime_checkable
class SupportsLt[T](Protocol):
    def __lt__(self, other: T) -> bool: ...


@runtime_checkable
class SupportsLe[T](Protocol):
    def __le__(self, other: T) -> bool: ...


@runtime_checkable
class SupportsGt[T](Protocol):
    def __gt__(self, other: T) -> bool: ...


@runtime_checkable
class SupportsGe[T](Protocol):
    def __ge__(self, other: T) -> bool: ...
