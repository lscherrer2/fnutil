# fnutil

Lightweight functional-style helpers for Python 3.13+.

Provides two composable primitives:

- **`Expression[T]`** — wraps a single value in a chainable, Option-aware monad with arithmetic and comparison operators.
- **`Iterator[T]`** — wraps any iterable with a lazy, chainable adapter API modelled on Rust's `Iterator` trait.

## Installation

```
pip install fnutil
```

```
uv add fnutil
```

## Quick start

```python
from fnutil import expr, it

# Expression: wrap → transform → unwrap
result = (
    expr(10)
    .map(lambda x: x * 2)
    .filter(lambda x: x > 15)
    .unwrap_or(0)
)
assert result == 20

# Iterator: wrap → chain lazy adapters → collect
total = (
    it(range(10))
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x ** 2)
    .fold(0, lambda acc, x: acc + x)
)
assert total == 120
```

## `Expression[T]`

```python
from fnutil import expr
```

### Construction

```python
e = expr(42)        # Expression[int]
e = expr(None)      # Expression[None]
e = expr([1, 2, 3]) # Expression[list[int]]
```

### Transform

| Method | Description |
|---|---|
| `.map(fn)` | Apply `fn` to the value; return `Expression[U]` |
| `.flat_map(fn)` | Apply `fn` which returns `Expression[U]`; unwrap one level |
| `.pipe(f, g, h)` | Thread value through functions left-to-right; equivalent to `expr(h(g(f(x))))` |
| `.then(fn)` | Apply `fn` and return the **raw** result (exits the monad) |
| `.inspect(fn)` | Call `fn` for side-effects; return `self` unchanged |

### Option-like

| Method / Property | Description |
|---|---|
| `.is_some` | `True` when value is not `None` |
| `.is_none` | `True` when value is `None` |
| `.filter(fn)` | Return `self` if `fn(value)` is truthy, else `Expression(None)` |
| `.or_else(default)` | Return `self` when `is_some`, else `Expression(default)` |
| `.or_else_with(fn)` | Return `self` when `is_some`, else `Expression(fn())` |
| `.unwrap_or(default)` | Return inner value when `is_some`, else `default` (raw) |

### Iterator interop

```python
expr([1, 2, 3]).iter()   # → Iterator[int]
expr(range(5)).iter()    # → Iterator[int]
```

### Operators

Arithmetic and comparison operators delegate to the inner value. Both operands must be `Expression` instances.

```python
expr(3) + expr(4)   # Expression(7)
expr(10) / expr(4)  # Expression(2.5)
expr(2) ** expr(8)  # Expression(256)
-expr(5)            # Expression(-5)
abs(expr(-7))       # Expression(7)

expr(1) < expr(2)   # True
expr(3) >= expr(3)  # True
sorted([expr(3), expr(1), expr(2)])  # [Expression(1), Expression(2), Expression(3)]
```

### Equality

`Expression` equality compares inner values. Comparing with a raw value returns `False`.

```python
expr(1) == expr(1)  # True
expr(1) == 1        # False
```

---

## `Iterator[T]`

```python
from fnutil import it
```

### Construction

```python
it([1, 2, 3])
it(range(10))
it(x for x in some_generator())
```

### Lazy adapters (return `Iterator[T]`)

| Method | Description |
|---|---|
| `.filter(fn)` | Keep elements where `fn` is truthy |
| `.map(fn)` | Transform each element |
| `.enumerate()` | Yield `(index, element)` tuples |
| `.zip(other)` | Zip with another iterable (truncates to shortest) |
| `.zip_longest(other, fillvalue=None)` | Zip, padding the shorter side |
| `.chain(other)` | Concatenate another iterable |
| `.take(n)` | First `n` elements |
| `.skip(n)` | Skip first `n` elements |
| `.take_while(fn)` | Take elements while `fn` is truthy |
| `.skip_while(fn)` | Skip elements while `fn` is truthy |
| `.flat_map(fn)` | Map `fn` then flatten one level |
| `.flatten()` | Flatten one level of nesting |
| `.inspect(fn)` | Side-effect on each element; pass through unchanged |
| `.filter_false(fn)` | Keep elements where `fn` is falsy |
| `.accumulate(fn=None, *, initial=None)` | Running accumulated values |
| `.cycle()` | Repeat endlessly |
| `.batched(n)` | Non-overlapping tuples of length `n` |
| `.pairwise()` | Successive overlapping pairs |
| `.compress(selectors)` | Keep elements whose selector is truthy |
| `.starmap(fn)` | Unpack each element as `fn(*item)` |
| `.group_by(fn=None)` | Group consecutive elements by key |
| `[i]` / `[start:stop:step]` | Integer index (take) or slice (islice) |

### Consuming terminators (exhaust and return a value)

| Method | Returns | Description |
|---|---|---|
| `.collect(factory)` | `U` | e.g. `.collect(list)`, `.collect(set)` |
| `.collect_expr(factory)` | `Expression[U]` | Same, wrapped in `Expression` |
| `.fold(init, fn)` | `U` | Left-fold with initial value |
| `.reduce(fn)` | `T \| None` | Left-fold without init; `None` on empty |
| `.for_each(fn)` | `None` | Consume, calling `fn` on each element |
| `.count()` | `int` | Number of elements |
| `.find(fn)` | `T \| None` | First element where `fn` is truthy |
| `.any(fn)` | `bool` | True if any element satisfies `fn` |
| `.all(fn)` | `bool` | True if all elements satisfy `fn` |
| `.min()` | `T \| None` | Minimum element; `None` if empty |
| `.max()` | `T \| None` | Maximum element; `None` if empty |
| `.nth(n)` | `T \| None` | Element at zero-based index `n`; `None` if out of range |
| `.last()` | `T \| None` | Last element; `None` if empty |
| `.partition(fn)` | `(list[T], list[T])` | `(truthy, falsy)` split |
| `.value` | `Iterable[T]` | Raw underlying iterable |

### Examples

```python
from fnutil import it

# Collect into a list
it([1, 2, 3]).map(lambda x: x * 2).collect(list)
# [2, 4, 6]

# Group consecutive words by first letter
words = ["ant", "bee", "bat", "cat"]
for letter, group in it(sorted(words)).group_by(lambda w: w[0]):
    print(letter, group.collect(list))
# a ['ant']
# b ['bat', 'bee']
# c ['cat']

# Batch into chunks
it(range(7)).batched(3).collect(list)
# [(0, 1, 2), (3, 4, 5), (6,)]

# Combine with Expression
it(range(10)).filter(lambda x: x % 2 == 0).collect_expr(list)
# Expression([0, 2, 4, 6, 8])
```

---

## Type checking

`fnutil` ships a `py.typed` marker and `.pyi` stub files for all modules. It is fully compatible with Pyright and mypy.

## Requirements

- Python 3.13+
- No runtime dependencies

## License

MIT
