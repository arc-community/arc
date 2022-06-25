#!/usr/bin/env python3

from pathlib import Path

import pytest

import arc.eval
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
