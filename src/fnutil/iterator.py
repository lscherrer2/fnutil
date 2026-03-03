from __future__ import annotations

import builtins
import functools
import itertools
from collections import deque
from collections.abc import Callable, Iterable

from fnutil.expression import Expression, expr


def it[T](iterable: Iterable[T]) -> Iterator[T]:
    return Iterator(iterable=iterable)


class Iterator[T]:
    def __init__(self, iterable: Iterable[T]):
        self._inner = iterable

    def __iter__(self):
        return builtins.iter(self._inner)

    def __getitem__(self, index: int | slice) -> Iterator[T]:
        if isinstance(index, int):
            return it(itertools.islice(self._inner, index))
        if isinstance(index, slice):
            return it(itertools.islice(self._inner, index.start, index.stop, index.step))
        raise TypeError(f"Iterator indices must be integers or slices, not {type(index).__name__}")

    def filter(self, fn: Callable[[T], bool]) -> Iterator[T]:
        return it(builtins.filter(fn, self._inner))

    def map[U](self, fn: Callable[[T], U]) -> Iterator[U]:
        return it(builtins.map(fn, self._inner))

    def enumerate(self) -> Iterator[tuple[int, T]]:
        return it(builtins.enumerate(self._inner))

    def zip[U](self, other: Iterable[U]) -> Iterator[tuple[T, U]]:
        return it(builtins.zip(self._inner, other, strict=False))

    def chain(self, other: Iterable[T]) -> Iterator[T]:
        return it(itertools.chain(self._inner, other))

    def take(self, n: int) -> Iterator[T]:
        return it(itertools.islice(self._inner, n))

    def skip(self, n: int) -> Iterator[T]:
        return it(itertools.islice(self._inner, n, None))

    def take_while(self, fn: Callable[[T], bool]) -> Iterator[T]:
        return it(itertools.takewhile(fn, self._inner))

    def skip_while(self, fn: Callable[[T], bool]) -> Iterator[T]:
        return it(itertools.dropwhile(fn, self._inner))

    def flat_map[U](self, fn: Callable[[T], Iterable[U]]) -> Iterator[U]:
        return it(itertools.chain.from_iterable(builtins.map(fn, self._inner)))

    def flatten[U](self) -> Iterator[U]:  # pyright: ignore[reportInvalidTypeVarUse]
        return it(itertools.chain.from_iterable(self._inner))  # type: ignore[arg-type]

    def inspect(self, fn: Callable[[T], None]) -> Iterator[T]:
        def _inspect(iterable: Iterable[T]):
            for item in iterable:
                fn(item)
                yield item

        return it(_inspect(self._inner))

    def filter_false(self, fn: Callable[[T], bool]) -> Iterator[T]:
        """Yield elements for which *fn* returns False (inverse of filter)."""
        return it(itertools.filterfalse(fn, self._inner))

    def accumulate(
        self,
        fn: Callable[[T, T], T] | None = None,
        *,
        initial: T | None = None,
    ) -> Iterator[T]:
        """Yield running accumulated values (default: running sum).

        Mirrors ``itertools.accumulate``. Pass a binary *fn* for custom
        accumulation (e.g. ``operator.mul`` for a running product).
        """
        return it(itertools.accumulate(self._inner, fn, initial=initial))  # type: ignore[arg-type]

    def cycle(self) -> Iterator[T]:
        """Repeat the sequence endlessly."""
        return it(itertools.cycle(self._inner))

    def batched(self, n: int) -> Iterator[tuple[T, ...]]:
        """Chunk into non-overlapping tuples of length *n*.

        The last tuple may be shorter if the iterable length is not a
        multiple of *n*.
        """
        return it(itertools.batched(self._inner, n, strict=False))  # type: ignore[arg-type]

    def pairwise(self) -> Iterator[tuple[T, T]]:
        """Yield successive overlapping pairs: (s[0],s[1]), (s[1],s[2]), …"""
        return it(itertools.pairwise(self._inner))  # type: ignore[return-value]

    def compress(self, selectors: Iterable) -> Iterator[T]:
        """Keep only elements whose corresponding selector is truthy."""
        return it(itertools.compress(self._inner, selectors))

    def zip_longest[U](
        self, other: Iterable[U], fillvalue: T | U | None = None
    ) -> Iterator[tuple[T | None, U | None]]:
        """Zip, padding the shorter side with *fillvalue* instead of truncating."""
        return it(itertools.zip_longest(self._inner, other, fillvalue=fillvalue))  # type: ignore[return-value]

    def starmap[U](self, fn: Callable[..., U]) -> Iterator[U]:
        """Map *fn* over the iterator, unpacking each element as ``fn(*item)``.

        Useful when elements are already tuples of arguments, e.g.::

            it([(2, 5), (3, 2)]).starmap(pow)  # → 32, 9
        """
        return it(itertools.starmap(fn, self._inner))  # type: ignore[arg-type]

    def group_by[K](self, fn: Callable[[T], K] | None = None) -> Iterator[tuple[K, Iterator[T]]]:
        """Group consecutive elements by key function *fn*.

        Mirrors ``itertools.groupby``: the input should be sorted on the
        same key for a meaningful result.  Each yielded value is
        ``(key, sub_iterator)``.
        """

        def _wrap(groups):
            for key, group in groups:
                yield key, it(group)

        return it(_wrap(itertools.groupby(self._inner, fn)))  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Consuming terminators – exhaust the iterator and return a value
    # ------------------------------------------------------------------

    def fold[U](self, init: U, fn: Callable[[U, T], U]) -> U:
        return functools.reduce(fn, self._inner, init)

    def reduce(self, fn: Callable[[T, T], T]) -> T | None:
        try:
            return functools.reduce(fn, self._inner)
        except TypeError:
            # functools.reduce raises TypeError on empty sequence with no initializer
            return None

    def for_each(self, fn: Callable[[T], None]) -> None:
        for item in self._inner:
            fn(item)

    def count(self) -> int:
        return builtins.sum(1 for _ in self._inner)

    def find(self, fn: Callable[[T], bool]) -> T | None:
        return builtins.next(builtins.filter(fn, self._inner), None)

    def any(self, fn: Callable[[T], bool]) -> bool:
        return builtins.any(fn(item) for item in self._inner)

    def all(self, fn: Callable[[T], bool]) -> bool:
        return builtins.all(fn(item) for item in self._inner)

    def min(self) -> T | None:
        try:
            return builtins.min(self._inner)  # type: ignore[type-var]
        except ValueError:
            return None

    def max(self) -> T | None:
        try:
            return builtins.max(self._inner)  # type: ignore[type-var]
        except ValueError:
            return None

    def nth(self, n: int) -> T | None:
        return builtins.next(itertools.islice(self._inner, n, None), None)

    def last(self) -> T | None:
        d: deque[T] = deque(self._inner, maxlen=1)
        return d[0] if d else None

    def partition(self, fn: Callable[[T], bool]) -> tuple[list[T], list[T]]:
        yes: list[T] = []
        no: list[T] = []
        for item in self._inner:
            (yes if fn(item) else no).append(item)
        return yes, no

    def collect[U](self, factory: Callable[[Iterable[T]], U]) -> U:
        return factory(self._inner)

    def collect_expr[U](self, factory: Callable[[Iterable[T]], U]) -> Expression[U]:
        return expr(factory(self._inner))

    @property
    def value(self) -> Iterable[T]:
        return self._inner
