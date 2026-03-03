from __future__ import annotations

from fnutil.expression import Expression, expr


class TestConstruction:
    def test_value_property(self):
        assert expr(42).value == 42

    def test_value_none(self):
        assert expr(None).value is None

    def test_value_string(self):
        assert expr("hello").value == "hello"

    def test_value_list(self):
        assert expr([1, 2, 3]).value == [1, 2, 3]


class TestReprAndEquality:
    def test_repr(self):
        assert repr(expr(1)) == "Expression(1)"

    def test_repr_string(self):
        assert repr(expr("hi")) == "Expression('hi')"

    def test_repr_none(self):
        assert repr(expr(None)) == "Expression(None)"

    def test_eq_same_value(self):
        assert expr(1) == expr(1)

    def test_eq_different_value(self):
        assert expr(1) != expr(2)

    def test_eq_not_raw_value(self):
        assert (expr(1) == 1) is False

    def test_eq_not_raw_string(self):
        assert (expr("x") == "x") is False

    def test_hash_equal_objects(self):
        assert hash(expr(5)) == hash(expr(5))

    def test_hash_usable_in_set(self):
        s = {expr(1), expr(2), expr(1)}
        assert len(s) == 2


class TestMap:
    def test_map_int(self):
        assert expr(3).map(lambda x: x * 2) == expr(6)

    def test_map_to_string(self):
        assert expr(10).map(str) == expr("10")

    def test_map_chained(self):
        result = expr(1).map(lambda x: x + 1).map(lambda x: x * 3)
        assert result == expr(6)

    def test_map_on_none(self):
        assert expr(None).map(lambda x: 42) == expr(42)


class TestFlatMap:
    def test_flat_map_basic(self):
        result = expr(3).flat_map(lambda x: expr(x * 10))
        assert result == expr(30)

    def test_flat_map_chained(self):
        result = expr(2).flat_map(lambda x: expr(x + 1)).flat_map(lambda x: expr(x * 4))
        assert result == expr(12)

    def test_flat_map_returns_none_expr(self):
        result = expr(5).flat_map(lambda _: expr(None))
        assert result == expr(None)


class TestPipe:
    def test_pipe_single(self):
        assert expr(4).pipe(lambda x: x + 1) == expr(5)

    def test_pipe_multiple(self):
        result = expr(1).pipe(
            lambda x: x + 1,  # 2
            lambda x: x * 3,  # 6
            lambda x: x - 1,  # 5
        )
        assert result == expr(5)

    def test_pipe_no_fns(self):
        assert expr(7).pipe() == expr(7)

    def test_pipe_type_change(self):
        result = expr(10).pipe(str, lambda s: s + "!")
        assert result == expr("10!")


class TestThen:
    def test_then_returns_raw(self):
        result = expr(5).then(lambda x: x * 2)
        assert result == 10
        assert not isinstance(result, Expression)

    def test_then_to_string(self):
        assert expr(99).then(str) == "99"


class TestInspect:
    def test_inspect_side_effect(self):
        seen = []
        result = expr(42).inspect(seen.append)
        assert seen == [42]
        assert result == expr(42)

    def test_inspect_returns_self(self):
        e = expr(7)
        assert e.inspect(lambda _: None) is e


class TestIsSomeIsNone:
    def test_is_some_with_value(self):
        assert expr(0).is_some is True

    def test_is_some_with_false(self):
        assert expr(False).is_some is True

    def test_is_some_with_none(self):
        assert expr(None).is_some is False

    def test_is_none_with_value(self):
        assert expr(1).is_none is False

    def test_is_none_with_none(self):
        assert expr(None).is_none is True


class TestFilter:
    def test_filter_passes(self):
        result = expr(10).filter(lambda x: x > 5)
        assert result == expr(10)

    def test_filter_fails(self):
        result = expr(3).filter(lambda x: x > 5)
        assert result == expr(None)

    def test_filter_on_none(self):
        result = expr(None).filter(lambda x: x is None)
        assert result == expr(None)


class TestOrElse:
    def test_or_else_some(self):
        assert expr(5).or_else(99) == expr(5)

    def test_or_else_none(self):
        assert expr(None).or_else(99) == expr(99)

    def test_or_else_zero_is_some(self):
        assert expr(0).or_else(99) == expr(0)

    def test_or_else_false_is_some(self):
        assert expr(False).or_else(99) == expr(False)


class TestOrElseWith:
    def test_or_else_with_some(self):
        called = []
        result = expr(5).or_else_with(lambda: called.append(1) or 99)
        assert result == expr(5)
        assert called == []  # factory not called

    def test_or_else_with_none(self):
        result = expr(None).or_else_with(lambda: 42)
        assert result == expr(42)

    def test_or_else_with_zero_is_some(self):
        result = expr(0).or_else_with(lambda: 99)
        assert result == expr(0)


class TestUnwrapOr:
    def test_unwrap_or_some(self):
        assert expr(7).unwrap_or(0) == 7

    def test_unwrap_or_none(self):
        assert expr(None).unwrap_or(0) == 0

    def test_unwrap_or_zero_is_some(self):
        assert expr(0).unwrap_or(99) == 0


class TestIter:
    def test_iter_from_list(self):
        from fnutil.iterator import Iterator

        result = expr([1, 2, 3]).iter()
        assert isinstance(result, Iterator)
        assert result.collect(list) == [1, 2, 3]

    def test_iter_from_range(self):
        result = expr(range(5)).iter().collect(list)
        assert result == [0, 1, 2, 3, 4]


class TestArithmetic:
    def test_add(self):
        assert expr(3) + expr(4) == expr(7)

    def test_sub(self):
        assert expr(10) - expr(3) == expr(7)

    def test_mul(self):
        assert expr(6) * expr(7) == expr(42)

    def test_truediv(self):
        assert expr(10) / expr(4) == expr(2.5)

    def test_floordiv(self):
        assert expr(10) // expr(3) == expr(3)

    def test_mod(self):
        assert expr(10) % expr(3) == expr(1)

    def test_pow(self):
        assert expr(2) ** expr(8) == expr(256)

    def test_neg(self):
        assert -expr(5) == expr(-5)

    def test_neg_already_negative(self):
        assert -expr(-3) == expr(3)

    def test_abs_positive(self):
        assert abs(expr(4)) == expr(4)

    def test_abs_negative(self):
        assert abs(expr(-7)) == expr(7)

    def test_add_floats(self):
        assert expr(1.5) + expr(2.5) == expr(4.0)

    def test_add_strings(self):
        assert expr("hello, ") + expr("world") == expr("hello, world")


class TestComparison:
    def test_lt_true(self):
        assert (expr(1) < expr(2)) is True

    def test_lt_false(self):
        assert (expr(2) < expr(1)) is False

    def test_le_equal(self):
        assert (expr(3) <= expr(3)) is True

    def test_le_less(self):
        assert (expr(2) <= expr(3)) is True

    def test_le_greater(self):
        assert (expr(4) <= expr(3)) is False

    def test_gt_true(self):
        assert (expr(5) > expr(2)) is True

    def test_gt_false(self):
        assert (expr(1) > expr(2)) is False

    def test_ge_equal(self):
        assert (expr(3) >= expr(3)) is True

    def test_ge_greater(self):
        assert (expr(4) >= expr(3)) is True

    def test_ge_less(self):
        assert (expr(2) >= expr(3)) is False

    def test_comparison_strings(self):
        assert (expr("apple") < expr("banana")) is True

    def test_sort_with_expressions(self):
        items = [expr(3), expr(1), expr(2)]
        assert sorted(items) == [expr(1), expr(2), expr(3)]


class TestIntegration:
    def test_chain_map_filter_unwrap(self):
        result = expr(10).map(lambda x: x * 2).filter(lambda x: x > 15).unwrap_or(0)
        assert result == 20

    def test_chain_map_filter_miss_unwrap(self):
        result = expr(5).map(lambda x: x * 2).filter(lambda x: x > 15).unwrap_or(0)
        assert result == 0

    def test_arithmetic_chain(self):
        result = (expr(2) + expr(3)) * expr(4)
        assert result == expr(20)

    def test_pipe_then_combo(self):
        result = expr(3).pipe(lambda x: x**2, lambda x: x + 1).then(str)
        assert result == "10"

    def test_or_else_chain(self):
        result = expr(None).or_else(5).map(lambda x: x * 2)  # type: ignore[operator]
        assert result == expr(10)
