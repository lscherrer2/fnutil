from __future__ import annotations

import pytest

from fnutil.iterator import it as fn_it


def collect(it) -> list:
    return list(it)


class TestMap:
    def test_map_doubles(self):
        result = fn_it([1, 2, 3]).map(lambda x: x * 2).collect(list)
        assert result == [2, 4, 6]

    def test_map_to_string(self):
        result = fn_it([1, 2, 3]).map(str).collect(list)
        assert result == ["1", "2", "3"]

    def test_map_empty(self):
        assert fn_it([]).map(lambda x: x).collect(list) == []


class TestFilter:
    def test_filter_evens(self):
        result = (
            fn_it([1, 2, 3, 4, 5]).filter(lambda x: x % 2 == 0).collect(list)
        )
        assert result == [2, 4]

    def test_filter_empty(self):
        assert fn_it([]).filter(lambda x: True).collect(list) == []


class TestEnumerate:
    def test_enumerate_basic(self):
        result = fn_it(["a", "b", "c"]).enumerate().collect(list)
        assert result == [(0, "a"), (1, "b"), (2, "c")]

    def test_enumerate_empty(self):
        assert fn_it([]).enumerate().collect(list) == []


class TestZip:
    def test_zip_basic(self):
        result = fn_it([1, 2, 3]).zip([4, 5, 6]).collect(list)
        assert result == [(1, 4), (2, 5), (3, 6)]

    def test_zip_truncates_to_shorter(self):
        result = fn_it([1, 2, 3]).zip([10, 20]).collect(list)
        assert result == [(1, 10), (2, 20)]

    def test_zip_empty(self):
        assert fn_it([]).zip([1, 2]).collect(list) == []


class TestChain:
    def test_chain_two_lists(self):
        result = fn_it([1, 2]).chain([3, 4]).collect(list)
        assert result == [1, 2, 3, 4]

    def test_chain_empty_left(self):
        assert fn_it([]).chain([1, 2]).collect(list) == [1, 2]

    def test_chain_empty_right(self):
        assert fn_it([1, 2]).chain([]).collect(list) == [1, 2]


class TestTake:
    def test_take_first_n(self):
        assert fn_it([1, 2, 3, 4, 5]).take(3).collect(list) == [1, 2, 3]

    def test_take_more_than_available(self):
        assert fn_it([1, 2]).take(10).collect(list) == [1, 2]

    def test_take_zero(self):
        assert fn_it([1, 2, 3]).take(0).collect(list) == []


class TestSkip:
    def test_skip_first_n(self):
        assert fn_it([1, 2, 3, 4, 5]).skip(2).collect(list) == [3, 4, 5]

    def test_skip_more_than_available(self):
        assert fn_it([1, 2]).skip(10).collect(list) == []

    def test_skip_zero(self):
        assert fn_it([1, 2, 3]).skip(0).collect(list) == [1, 2, 3]


class TestTakeWhile:
    def test_take_while_less_than_3(self):
        assert fn_it([1, 2, 3, 4]).take_while(lambda x: x < 3).collect(
            list
        ) == [1, 2]

    def test_take_while_none(self):
        assert fn_it([5, 6, 7]).take_while(lambda x: x < 3).collect(list) == []

    def test_take_while_all(self):
        assert fn_it([1, 2]).take_while(lambda x: x < 10).collect(list) == [
            1,
            2,
        ]


class TestSkipWhile:
    def test_skip_while_less_than_3(self):
        assert fn_it([1, 2, 3, 4]).skip_while(lambda x: x < 3).collect(
            list
        ) == [3, 4]

    def test_skip_while_all(self):
        assert fn_it([1, 2]).skip_while(lambda x: x < 10).collect(list) == []

    def test_skip_while_none(self):
        assert fn_it([5, 6]).skip_while(lambda x: x < 3).collect(list) == [
            5,
            6,
        ]


class TestFlatMap:
    def test_flat_map_duplicate(self):
        result = fn_it([1, 2, 3]).flat_map(lambda x: [x, x]).collect(list)
        assert result == [1, 1, 2, 2, 3, 3]

    def test_flat_map_empty_inner(self):
        assert fn_it([1, 2, 3]).flat_map(lambda x: []).collect(list) == []

    def test_flat_map_empty_outer(self):
        assert fn_it([]).flat_map(lambda x: [x]).collect(list) == []


class TestFlatten:
    def test_flatten_basic(self):
        result = fn_it([[1, 2], [3, 4], [5]]).flatten().collect(list)
        assert result == [1, 2, 3, 4, 5]

    def test_flatten_empty_inner(self):
        assert fn_it([[], []]).flatten().collect(list) == []

    def test_flatten_empty_outer(self):
        assert fn_it([]).flatten().collect(list) == []


class TestInspect:
    def test_inspect_side_effect(self):
        seen = []
        result = fn_it([1, 2, 3]).inspect(seen.append).collect(list)
        assert result == [1, 2, 3]
        assert seen == [1, 2, 3]

    def test_inspect_does_not_alter_values(self):
        result = fn_it([10, 20]).inspect(lambda x: None).collect(list)
        assert result == [10, 20]


class TestFold:
    def test_fold_sum(self):
        assert fn_it([1, 2, 3, 4]).fold(0, lambda acc, x: acc + x) == 10

    def test_fold_empty_returns_init(self):
        assert fn_it([]).fold(42, lambda acc, x: acc + x) == 42

    def test_fold_string_concat(self):
        assert fn_it(["a", "b", "c"]).fold("", lambda acc, x: acc + x) == "abc"


class TestReduce:
    def test_reduce_sum(self):
        assert fn_it([1, 2, 3, 4]).reduce(lambda a, b: a + b) == 10

    def test_reduce_single(self):
        assert fn_it([7]).reduce(lambda a, b: a + b) == 7

    def test_reduce_empty_returns_none(self):
        assert fn_it([]).reduce(lambda a, b: a + b) is None


class TestForEach:
    def test_for_each_side_effects(self):
        seen = []
        fn_it([1, 2, 3]).for_each(seen.append)
        assert seen == [1, 2, 3]

    def test_for_each_empty(self):
        seen = []
        fn_it([]).for_each(seen.append)
        assert seen == []


class TestCount:
    def test_count_basic(self):
        assert fn_it([1, 2, 3]).count() == 3

    def test_count_empty(self):
        assert fn_it([]).count() == 0


class TestFind:
    def test_find_first_even(self):
        assert fn_it([1, 3, 4, 5, 6]).find(lambda x: x % 2 == 0) == 4

    def test_find_none_match(self):
        assert fn_it([1, 3, 5]).find(lambda x: x % 2 == 0) is None

    def test_find_empty(self):
        assert fn_it([]).find(lambda x: True) is None


class TestAny:
    def test_any_true(self):
        assert fn_it([1, 2, 3]).any(lambda x: x > 2) is True

    def test_any_false(self):
        assert fn_it([1, 2, 3]).any(lambda x: x > 10) is False

    def test_any_empty(self):
        assert fn_it([]).any(lambda x: True) is False


class TestAll:
    def test_all_true(self):
        assert fn_it([2, 4, 6]).all(lambda x: x % 2 == 0) is True

    def test_all_false(self):
        assert fn_it([2, 3, 6]).all(lambda x: x % 2 == 0) is False

    def test_all_empty(self):
        assert fn_it([]).all(lambda x: False) is True


class TestMin:
    def test_min_basic(self):
        assert fn_it([3, 1, 2]).min() == 1

    def test_min_empty(self):
        assert fn_it([]).min() is None

    def test_min_single(self):
        assert fn_it([42]).min() == 42


class TestMax:
    def test_max_basic(self):
        assert fn_it([3, 1, 2]).max() == 3

    def test_max_empty(self):
        assert fn_it([]).max() is None

    def test_max_single(self):
        assert fn_it([42]).max() == 42


class TestNth:
    def test_nth_zero(self):
        assert fn_it([10, 20, 30]).nth(0) == 10

    def test_nth_second(self):
        assert fn_it([10, 20, 30]).nth(1) == 20

    def test_nth_out_of_range(self):
        assert fn_it([10, 20]).nth(5) is None

    def test_nth_empty(self):
        assert fn_it([]).nth(0) is None


class TestLast:
    def test_last_basic(self):
        assert fn_it([1, 2, 3]).last() == 3

    def test_last_single(self):
        assert fn_it([99]).last() == 99

    def test_last_empty(self):
        assert fn_it([]).last() is None


class TestPartition:
    def test_partition_evens_odds(self):
        evens, odds = fn_it([1, 2, 3, 4, 5]).partition(lambda x: x % 2 == 0)
        assert evens == [2, 4]
        assert odds == [1, 3, 5]

    def test_partition_all_true(self):
        yes, no = fn_it([2, 4]).partition(lambda x: x % 2 == 0)
        assert yes == [2, 4]
        assert no == []

    def test_partition_all_false(self):
        yes, no = fn_it([1, 3]).partition(lambda x: x % 2 == 0)
        assert yes == []
        assert no == [1, 3]

    def test_partition_empty(self):
        yes, no = fn_it([]).partition(lambda x: True)
        assert yes == []
        assert no == []


class TestCollect:
    def test_collect_to_list(self):
        assert fn_it([1, 2, 3]).collect(list) == [1, 2, 3]

    def test_collect_to_set(self):
        assert fn_it([1, 2, 2, 3]).collect(set) == {1, 2, 3}

    def test_collect_to_tuple(self):
        assert fn_it([1, 2, 3]).collect(tuple) == (1, 2, 3)


class TestChaining:
    def test_filter_map_collect(self):
        result = (
            fn_it([1, 2, 3, 4, 5])
            .filter(lambda x: x % 2 == 0)
            .map(lambda x: x * 10)
            .collect(list)
        )
        assert result == [20, 40]

    def test_skip_take_collect(self):
        result = fn_it(range(10)).skip(3).take(4).collect(list)
        assert result == [3, 4, 5, 6]

    def test_flat_map_filter_collect(self):
        result = (
            fn_it([[1, 2], [3, 4], [5]])
            .flatten()
            .filter(lambda x: x % 2 != 0)
            .collect(list)
        )
        assert result == [1, 3, 5]


class TestGetItem:
    def test_int_index_is_take(self):
        assert fn_it(range(10))[3].collect(list) == [0, 1, 2]

    def test_slice_start_stop(self):
        assert fn_it(range(10))[2:5].collect(list) == [2, 3, 4]

    def test_slice_stop_only(self):
        assert fn_it(range(10))[:4].collect(list) == [0, 1, 2, 3]

    def test_slice_start_only(self):
        assert fn_it(range(5))[2:].collect(list) == [2, 3, 4]

    def test_slice_step(self):
        assert fn_it(range(10))[::2].collect(list) == [0, 2, 4, 6, 8]

    def test_slice_start_stop_step(self):
        assert fn_it(range(10))[1:8:3].collect(list) == [1, 4, 7]

    def test_slice_empty_result(self):
        assert fn_it(range(5))[10:20].collect(list) == []

    def test_invalid_index_raises(self):
        with pytest.raises(TypeError):
            fn_it([1, 2, 3])["bad"]  # type: ignore[index]


class TestFilterFalse:
    def test_filter_false_odds(self):
        result = (
            fn_it([1, 2, 3, 4, 5])
            .filter_false(lambda x: x % 2 == 0)
            .collect(list)
        )
        assert result == [1, 3, 5]

    def test_filter_false_empty(self):
        assert fn_it([]).filter_false(lambda x: True).collect(list) == []

    def test_filter_false_none_pass(self):
        assert fn_it([1, 2, 3]).filter_false(lambda x: False).collect(
            list
        ) == [1, 2, 3]


class TestAccumulate:
    def test_accumulate_default_sum(self):
        assert fn_it([1, 2, 3, 4]).accumulate().collect(list) == [
            1,
            3,
            6,
            10,
        ]

    def test_accumulate_product(self):
        import operator

        assert fn_it([1, 2, 3, 4]).accumulate(operator.mul).collect(list) == [
            1,
            2,
            6,
            24,
        ]

    def test_accumulate_with_initial(self):
        assert fn_it([1, 2, 3]).accumulate(initial=10).collect(list) == [
            10,
            11,
            13,
            16,
        ]

    def test_accumulate_empty(self):
        assert fn_it([]).accumulate().collect(list) == []


class TestCycle:
    def test_cycle_take_repeats(self):
        result = fn_it([1, 2, 3]).cycle().take(7).collect(list)
        assert result == [1, 2, 3, 1, 2, 3, 1]

    def test_cycle_single_element(self):
        assert fn_it([42]).cycle().take(4).collect(list) == [42, 42, 42, 42]


class TestBatched:
    def test_batched_even(self):
        result = fn_it([1, 2, 3, 4, 5, 6]).batched(2).collect(list)
        assert result == [(1, 2), (3, 4), (5, 6)]

    def test_batched_remainder(self):
        result = fn_it([1, 2, 3, 4, 5]).batched(2).collect(list)
        assert result == [(1, 2), (3, 4), (5,)]

    def test_batched_larger_than_input(self):
        assert fn_it([1, 2]).batched(5).collect(list) == [(1, 2)]

    def test_batched_empty(self):
        assert fn_it([]).batched(3).collect(list) == []


class TestPairwise:
    def test_pairwise_basic(self):
        result = fn_it([1, 2, 3, 4]).pairwise().collect(list)
        assert result == [(1, 2), (2, 3), (3, 4)]

    def test_pairwise_single(self):
        assert fn_it([1]).pairwise().collect(list) == []

    def test_pairwise_empty(self):
        assert fn_it([]).pairwise().collect(list) == []


class TestCompress:
    def test_compress_basic(self):
        result = fn_it("ABCDEF").compress([1, 0, 1, 0, 1, 1]).collect(list)
        assert result == ["A", "C", "E", "F"]

    def test_compress_all_false(self):
        assert fn_it([1, 2, 3]).compress([0, 0, 0]).collect(list) == []

    def test_compress_all_true(self):
        assert fn_it([1, 2, 3]).compress([1, 1, 1]).collect(list) == [
            1,
            2,
            3,
        ]


class TestZipLongest:
    def test_zip_longest_pads_shorter(self):
        result = (
            fn_it([1, 2, 3]).zip_longest([10, 20], fillvalue=0).collect(list)
        )
        assert result == [(1, 10), (2, 20), (3, 0)]

    def test_zip_longest_equal_length(self):
        result = fn_it([1, 2]).zip_longest([3, 4]).collect(list)
        assert result == [(1, 3), (2, 4)]

    def test_zip_longest_empty_left(self):
        result = fn_it([]).zip_longest([1, 2], fillvalue=-1).collect(list)
        assert result == [(-1, 1), (-1, 2)]


class TestStarmap:
    def test_starmap_pow(self):
        result = fn_it([(2, 5), (3, 2), (10, 3)]).starmap(pow).collect(list)
        assert result == [32, 9, 1000]

    def test_starmap_add(self):
        import operator

        result = fn_it([(1, 2), (3, 4)]).starmap(operator.add).collect(list)
        assert result == [3, 7]

    def test_starmap_empty(self):
        assert fn_it([]).starmap(pow).collect(list) == []


class TestGroupBy:
    def test_group_by_consecutive(self):
        data = [1, 1, 2, 2, 3]
        groups = fn_it(data).group_by().collect(list)
        keys = [k for k, _ in groups]
        assert keys == [1, 2, 3]

    def test_group_by_with_key(self):
        data = ["apple", "ant", "banana", "berry", "cherry"]
        groups = fn_it(data).group_by(lambda s: s[0]).collect(list)
        keys = [k for k, _ in groups]
        assert keys == ["a", "b", "c"]

    def test_group_by_values(self):
        data = [1, 1, 2, 3, 3]
        result = {k: list(v) for k, v in fn_it(data).group_by()}
        assert result == {1: [1, 1], 2: [2], 3: [3, 3]}
