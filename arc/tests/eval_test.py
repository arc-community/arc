#!/usr/bin/env python3

from pathlib import Path

import pytest

import arc.eval
from arc import TaskData
from arc.agents.cheating_agent import CheatingAgent
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


def test_evaluate_agent_on_riddle(riddle1, task_data):
    agent = CheatingAgent()
    eval_result_list = arc.eval.evaluate_agent_on_riddles(agent, [riddle1], task_data)
    metric_result_dict = arc.eval.apply_metrics(
        eval_result_list, [BoardSizeMetric(), CorrectMetric()]
    )
    assert metric_result_dict["correct"].aggregate_result == 1.0
    assert "output" in eval_result_list.hints_accessed
