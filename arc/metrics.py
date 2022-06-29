#!/usr/bin/env python3

from __future__ import annotations

from typing import Any

import numpy as np

from arc.interface import BoardPair, EvalResult, Metric, TaskData, TopKList


class MinValMetric(Metric):
    def _get_value(
        self, test: BoardPair, task_data: TaskData, topk_list: TopKList
    ) -> float:
        raise NotImplementedError()

    def compute(self, eval_result: EvalResult) -> Any:
        values = [
            self._get_value(test, eval_result.task_data, topk_list)
            for test, topk_list in zip(eval_result.riddle.test, eval_result.solution)
        ]
        return min(values)


class MeanAggMetric(Metric):
    def aggregate(self, task_data: TaskData, results: list[Any]) -> Any:
        if not results:
            return 0
        return sum(results) / len(results)


class BoardSizeMetric(MinValMetric, MeanAggMetric):
    def __init__(self):
        super().__init__(name="board_size")

    def _get_value(
        self, test: BoardPair, task_data: TaskData, topk_list: TopKList
    ) -> float:
        if any(test.output.shape == b.shape for b in topk_list):
            return 1.0
        else:
            return 0.0


class CorrectMetric(MinValMetric, MeanAggMetric):
    def __init__(self):
        super().__init__(name="correct")

    def _get_value(
        self, test: BoardPair, task_data: TaskData, topk_list: TopKList
    ) -> float:
        def _allclose(a, b):
            if a.shape != b.shape:
                return 0.0
            return np.allclose(a, b)

        if any(_allclose(test.output.np, b.np) for b in topk_list):
            return 1.0
        else:
            return 0.0
