#!/usr/bin/env python3

from __future__ import annotations

from typing import Generic, TypeVar

import numpy as np
import pydantic
import pydantic.generics

from arc.interface import BoardPair, EvalResult, EvalResultList, TaskData, TopKList

T = TypeVar("T")


class MetricResult(pydantic.generics.GenericModel, Generic[T]):
    name: str
    compute_results: list[T]
    aggregate_result: T


MetricResultDict = dict[str, MetricResult]


class Metric(Generic[T]):
    def __init__(self, name: str):
        self.name = name

    def compute(self, eval_result: EvalResult) -> T:
        return self._compute(eval_result)

    def _compute(self, eval_result: EvalResult) -> T:
        raise NotImplementedError()

    def aggregate(
        self, eval_result_list: EvalResultList, compute_results: list[T]
    ) -> MetricResult[T]:
        aggregate_result = self._aggregate(eval_result_list, compute_results)
        result = MetricResult(
            name=self.name,
            compute_results=compute_results,
            aggregate_result=aggregate_result,
        )
        return result

    def _aggregate(
        self, eval_result_list: EvalResultList, compute_results: list[T]
    ) -> T:
        raise NotImplementedError()


class MinValMetric(Metric[float]):
    def _get_value(
        self, test: BoardPair, task_data: TaskData, topk_list: TopKList
    ) -> float:
        raise NotImplementedError()

    def _compute(self, eval_result: EvalResult) -> float:
        values = [
            self._get_value(test, eval_result.task_data, topk_list)
            for test, topk_list in zip(eval_result.riddle.test, eval_result.solution)
        ]
        return min(values)


class MeanAggMetric(Metric[float]):
    def _aggregate(
        self, eval_result_list: EvalResultList, compute_results: list[float]
    ) -> float:
        if not compute_results:
            return 0
        return sum(compute_results) / len(compute_results)


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


def get_default_metrics() -> list[Metric]:
    return [BoardSizeMetric(), CorrectMetric()]
