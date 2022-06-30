#!/usr/bin/env python3

import functools as fct
import itertools as itt
from typing import Callable

from arc.interface import Board, BoardPair, Riddle


def record_hint_access(f: Callable):
    @fct.wraps(f)
    def _recorded_f(self, *args, **kwargs):
        self._hints_accessed.add(f.__name__)
        return f(self, *args, **kwargs)

    return _recorded_f


class BoardHints:
    def __init__(
        self,
        riddle: Riddle,
        test_pair: BoardPair,
        hints_accessed: set[str],
    ):
        self._riddle = riddle
        self._test_pair = test_pair
        self._hints_accessed = hints_accessed

    @property
    def _test_output(self) -> Board:
        return self._test_pair.output

    @property
    @record_hint_access
    def output_shape(self):
        return self._test_output.shape

    @property
    @record_hint_access
    def output(self):
        return self._test_output

    @property
    @record_hint_access
    def num_colors(self):
        return len(set(self._test_output.data_flat))


class Hints:
    def __init__(self, riddle: Riddle):
        self._riddle = riddle
        self._hints_accessed = [set() for _ in riddle.test]

    @property
    def hints_accessed(self) -> set[str]:
        return set(itt.chain.from_iterable(self._hints_accessed))

    def board(self, test_idx) -> BoardHints:
        return BoardHints(
            riddle=self._riddle,
            test_pair=self._riddle.test[test_idx],
            hints_accessed=self._hints_accessed[test_idx],
        )
