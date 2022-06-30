#!/usr/bin/env python3

from pathlib import Path

import pytest

import arc.eval
from arc.agents import Agent
from arc.hints import BoardHints
from arc.interface import Board, BoardPair, TaskData, TopKList
from arc.metrics import BoardSizeMetric, CorrectMetric
from arc.settings import settings
from arc.utils import dataset


@pytest.fixture(scope="session", autouse=True)
def set_datadir():
    settings.dataset_dir = str(Path(__file__).parent / "test_data")


@pytest.fixture(scope="class")
def riddle1():
    return dataset.load_riddle_from_id(dataset.get_riddle_ids()[0])


@pytest.fixture(scope="class")
def task_data():
    return TaskData(topk=3)


def test_echo():
    assert True


def test_list_dir():
    assert dataset.get_riddle_ids()[0] == "t001"


class CheatingAgent(Agent):
    def solve_test_sample(
        self,
        task_data: TaskData,
        hints: BoardHints,
        train: list[BoardPair],
        test: Board,
        test_idx: int,
    ) -> TopKList:
        return TopKList([hints.output for _ in range(task_data.topk)])


def test_evaluate_agent_on_riddle(riddle1, task_data):
    agent = CheatingAgent()
    eval_results = arc.eval.evaluate_agent_on_riddles(agent, [riddle1], task_data)
    arc.eval.apply_metrics(eval_results, [BoardSizeMetric(), CorrectMetric()])
    assert eval_results.aggregation_results["correct"] == 1.0
    assert "output" in eval_results.hints_accessed
