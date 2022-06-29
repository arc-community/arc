#!/usr/bin/env python3

from pathlib import Path

import pytest

import arc.eval
from arc.interface import Agent, Board, Riddle, TaskData, TopKList
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
        self, riddle: Riddle, task_data: TaskData, test: Board
    ) -> TopKList:
        for t in riddle.test:
            if t.input == test:
                return TopKList([t.output for _ in range(task_data.topk)])
        else:
            assert False


def test_evaluate_agent_on_riddle(riddle1, task_data):
    agent = CheatingAgent()
    eval_results = arc.eval.evaluate_agent_on_riddles(agent, [riddle1], task_data)
    print(eval_results)
    # assert eval_result.score == 1.0
