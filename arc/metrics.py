#!/usr/bin/env python3

from __future__ import annotations

from typing import Callable, Generic, Optional, TypeVar

import numpy as np
import pydantic
import pydantic.generics

from arc.interface import Board, BoardPair, EvalResult, EvalResultList, TopKList

C = TypeVar("C")
A = TypeVar("A")


class MetricResult(pydantic.generics.GenericModel, Generic[C, A]):
    name: str
    compute_results: Optional[list[C]] = None
    aggregate_result: Optional[A] = None


MetricResultDict = dict[str, MetricResult]


def min_over_tests(
    eval_result: EvalResult, get_value: Callable[[BoardPair, TopKList], float]
) -> float:
    values = [
        get_value(test, topk_list)
        for test, topk_list in zip(eval_result.riddle.test, eval_result.solution)
    ]
    if not values:
        raise ValueError("No values for min computation.")
    return min(values)


class NotFoundError(Exception):
    pass


def get_correct_solution_idx(test_output: Board, topk_list: TopKList) -> int:
    for i, output in enumerate(topk_list):
        if safe_allclose(test_output.np, output.np):
            return i
    raise NotFoundError()


def safe_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def safe_allclose(a, b):
    if a.shape != b.shape:
        return 0.0
    return np.allclose(a, b)


class Metric(Generic[C, A]):
    def __init__(self, name: str):
        self.name = name

    def _compute(self, eval_result: EvalResult) -> C:
        raise NotImplementedError()

    def _aggregate(
        self, eval_result_list: EvalResultList, compute_results: list[C]
    ) -> A:
        raise NotImplementedError()

    def compute(self, eval_result: EvalResult) -> C:
        return self._compute(eval_result)

    def aggregate(
        self, eval_result_list: EvalResultList, compute_results: list[C]
    ) -> MetricResult[C, A]:
        aggregate_result = self._aggregate(eval_result_list, compute_results)
        result = MetricResult(
            name=self.name,
            compute_results=compute_results,
            aggregate_result=aggregate_result,
        )
        return result


METRICS = {}


def register_metric(metric: Metric):
    METRICS[metric.name] = metric


def get_metrics(names: list[str]) -> list[Metric]:
    return [METRICS[name] for name in names]


class MeanAggMetric(Metric[float, float]):
    def _aggregate(
        self, eval_result_list: EvalResultList, compute_results: list[float]
    ) -> float:
        return safe_mean(compute_results)


class BoardSizeMetric(MeanAggMetric, Metric[float, float]):
    def __init__(self):
        super().__init__(name="board_size")

    def _compute(self, eval_result: EvalResult) -> float:
        def _get_value(test: BoardPair, topk_list: TopKList) -> float:
            if any(test.output.shape == b.shape for b in topk_list):
                return 1.0
            else:
                return 0.0

        return min_over_tests(eval_result, _get_value)


register_metric(BoardSizeMetric())


class CorrectMetric(MeanAggMetric, Metric[float, float]):
    def __init__(self):
        super().__init__(name="correct")

    def _compute(self, eval_result: EvalResult) -> float:
        def _get_value(test: BoardPair, topk_list: TopKList) -> float:
            try:
                get_correct_solution_idx(test.output, topk_list)
                return 1.0
            except NotFoundError:
                return 0.0

        return min_over_tests(eval_result, _get_value)


register_metric(CorrectMetric())


class InverseRankOfCorrectMetric(Metric[float, float]):
    def __init__(self):
        super().__init__(name="inverse_rank_of_correct")

    def _compute(self, eval_result: EvalResult) -> float:
        def _get_value(test: BoardPair, topk_list: TopKList) -> float:
            try:
                idx = get_correct_solution_idx(test.output, topk_list)
                return 1.0 / (idx + 1)
            except NotFoundError:
                return 0.0

        return min_over_tests(eval_result, _get_value)

    def _aggregate(
        self, eval_result_list: EvalResultList, compute_results: list[float]
    ) -> float:
        return safe_mean([r for r in compute_results if r > 0.0])


register_metric(InverseRankOfCorrectMetric())


def get_default_metrics() -> list[Metric]:
    return get_metrics(["board_size", "correct"])
