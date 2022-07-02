#!/usr/bin/env python3

from arc.hints import BoardHints, Hints
from arc.interface import Board, BoardPair, RiddleSolution, TaskData, TopKList


class Agent:
    def __init__(self):
        pass

    def solve_riddle(
        self,
        task_data: TaskData,
        hints: Hints,
        train: list[BoardPair],
        test: list[Board],
    ) -> RiddleSolution:
        return [
            self.solve_test_sample(task_data, hints.board(idx), train, t, idx)
            for idx, t in enumerate(test)
        ]

    def solve_test_sample(
        self,
        task_data: TaskData,
        hints: BoardHints,
        train: list[BoardPair],
        test: Board,
        test_idx: int,
    ) -> TopKList:
        raise NotImplementedError()
