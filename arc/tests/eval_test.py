#!/usr/bin/env python3

from pathlib import Path

import pytest

import arc.eval
from arc import TaskData
from arc.agents.cheating_agent import CheatingAgent
from arc.metrics import get_default_metrics
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
    metrics = get_default_metrics()
    report = arc.eval.evaluate_and_report(agent, [riddle1], task_data, metrics=metrics)
    assert report.metric_results["correct"].aggregate_result == 1.0
    assert "output" in report.eval_results.hints_accessed
