#!/usr/bin/env python3

import tqdm
from loguru import logger

from arc.agents import Agent
from arc.hints import Hints
from arc.interface import EvalResult, EvalResultList, Riddle, TaskData
from arc.metrics import Metric, MetricResultDict
from arc.report import Report


def evaluate_agent_on_riddle(
    agent: Agent, riddle: Riddle, task_data: TaskData
) -> EvalResult:
    hints = Hints(riddle=riddle)
    solution = agent.solve_riddle(
        task_data=task_data, hints=hints, train=riddle.train, test=riddle.test_inputs
    )
    if (num_tests := len(riddle.test)) != (num_solutions := len(solution)):
        raise ValueError(
            f"Riddle has {num_tests} tests, but got {num_solutions} solutions."
        )
    expected_k = task_data.topk
    solution_ks = [len(sol) for sol in solution]
    if any(k != expected_k for k in solution_ks):
        raise ValueError(
            f"Expected all solutions to have k={expected_k} outputs,"
            f"but got {solution_ks}"
        )

    return EvalResult(
        riddle=riddle,
        task_data=task_data,
        solution=solution,
        hints_accessed=hints.hints_accessed,
    )


def evaluate_agent_on_riddles(agent: Agent, riddles: list[Riddle], task_data: TaskData):
    logger.info(f"Evaluating agent on {len(riddles)} riddles.")
    eval_results = [
        evaluate_agent_on_riddle(agent, riddle, task_data)
        for riddle in tqdm.tqdm(riddles)
    ]
    eval_result_list = EvalResultList(eval_results=eval_results, task_data=task_data)
    return eval_result_list


def apply_metrics(
    eval_result_list: EvalResultList, metrics: list[Metric]
) -> MetricResultDict:
    eval_results = eval_result_list.eval_results
    metric_results = MetricResultDict()
    for metric in metrics:
        logger.info(f"Applying metric {metric.name}.")
        compute_results = [
            metric.compute(eval_result) for eval_result in tqdm.tqdm(eval_results)
        ]
        metric_result = metric.aggregate(eval_result_list, compute_results)
        metric_results[metric.name] = metric_result
    return metric_results


def evaluate_and_report(
    agent: Agent,
    riddles: list[Riddle],
    task_data: TaskData,
    metrics: list[Metric] = None,
):
    eval_results = evaluate_agent_on_riddles(agent, riddles, task_data)
    if metrics is None:
        metrics = []
    metric_results = apply_metrics(eval_results, metrics)
    logger.info("Constructing report.")
    return Report(eval_results=eval_results, metric_results=metric_results)
