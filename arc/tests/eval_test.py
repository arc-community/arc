#!/usr/bin/env python3

from pathlib import Path

import pytest

import arc.eval
from arc.agents import Agent
from arc.interface import Board, BoardData, Riddle
from arc.settings import settings
from arc.utils import dataset


@pytest.fixture(scope="session", autouse=True)
def set_datadir():
    settings.dataset_dir = str(Path(__file__).parent / "test_data")


@pytest.fixture(scope="class", autouse=True)
def riddle1():
    return dataset.load_riddle_from_id(dataset.get_riddle_ids()[0])


def test_echo():
    assert True


def test_list_dir():
    assert dataset.get_riddle_ids()[0] == "t001"


def test_eval_solution_for_riddle(riddle1):
    eval_result = arc.eval.eval_solution_for_riddle(
        riddle1, [riddle1.test[0].output.data]
    )  # cheating
    assert eval_result.score == 1.0


class CheatingAgent(Agent):
    def solve_test_sample(self, riddle: Riddle, test: Board) -> BoardData:
        for t in riddle.test:
            if t.input == test:
                return t.output.data
        else:
            assert False


def test_evaluate_agent_on_riddle(riddle1):
    agent = CheatingAgent()
    eval_result = arc.eval.evaluate_agent_on_riddle(agent, riddle1)
    assert eval_result.score == 1.0
