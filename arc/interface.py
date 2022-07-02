#!/usr/bin/env python3

import itertools as itt
from typing import Optional

import numpy as np
import pydantic
from colored import attr, bg, fg

from arc.settings import settings

CELL_PADDING_STR = " " * settings.cell_padding
BOARD_GAP_STR = " " * settings.board_gap
PAIR_GAP_STR = "\n" + " " * settings.pair_gap + "\n"


class Board(pydantic.BaseModel):
    __root__: list[list[int]]

    @pydantic.validator("__root__", pre=True)
    def validate_native_list(cls, v):
        if isinstance(v, np.ndarray):
            v = v.tolist()
        return v

    @pydantic.validator("__root__")
    def validate_non_ragged(cls, v):
        if len(set(lengths := list(map(len, v)))) != 1:
            raise ValueError(
                f"All rows of a Board must be of same lengths, but got {lengths=}"
            )
        return v

    @property
    def data(self):
        return self.__root__

    @property
    def data_flat(self):
        return list(itt.chain.from_iterable(self.data))

    @property
    def np(self) -> np.ndarray:
        return np.array(self.data, dtype=np.int64)

    @property
    def num_rows(self) -> int:
        return len(self.data)

    @property
    def num_cols(self) -> int:
        return len(self.data[0])

    @property
    def shape(self) -> tuple[int, int]:
        return (self.num_rows, self.num_cols)

    @property
    def flat(self) -> list[int]:
        return list(itt.chain.from_iterable(self.data))

    @property
    def unique_values(self) -> set[int]:
        return set(self.flat)

    @property
    def num_unique_values(self) -> int:
        return len(self.unique_values)

    def fmt_cell(self, row: int, col: int, colored=False) -> str:
        value = self.data[row][col]
        value_str = f"{CELL_PADDING_STR}{value}{CELL_PADDING_STR}"
        if colored:
            return f"{fg(15)}{bg(value)}{value_str}{attr(0)}"
        else:
            return value_str

    def fmt_row(self, row: int, colored=False) -> str:
        return "".join(
            self.fmt_cell(row, col, colored=colored)
            for col in range(len(self.data[row]))
        )

    def fmt_empty_row(self):
        return "".join(
            f"{CELL_PADDING_STR} {CELL_PADDING_STR}" for _ in range(self.num_cols)
        )

    def fmt(self, colored=False) -> str:
        return "\n".join(
            self.fmt_row(row, colored=colored) for row in range(len(self.data))
        )


TopKList = list[Board]
RiddleSolution = list[TopKList]


class BoardPair(pydantic.BaseModel):
    input: Board
    output: Board

    def fmt(self, colored=False, with_output=True) -> str:
        rows = []
        max_row = (
            max(self.input.num_rows, self.output.num_rows)
            if with_output
            else self.input.num_rows
        )
        for row in range(max_row):
            row_parts = []
            if row >= self.input.num_rows:
                row_parts.append(self.input.fmt_empty_row())
            else:
                row_parts.append(self.input.fmt_row(row, colored=colored))
            if with_output:
                row_parts.append(BOARD_GAP_STR)
                if row >= self.output.num_rows:
                    row_parts.append(self.output.fmt_empty_row())
                else:
                    row_parts.append(self.output.fmt_row(row, colored=colored))
            rows.append("".join(row_parts))
        return "\n".join(rows)

    def as_np(self, with_solution=True):
        return (self.input.np, self.output.np if with_solution else None)


class Riddle(pydantic.BaseModel):
    train: list[BoardPair]
    test: list[BoardPair]
    riddle_id: Optional[str] = None
    subdir: Optional[str] = None

    def fmt(self, colored=False, with_test_outputs=False) -> str:
        parts = []
        if self.riddle_id:
            parts.append(f"ID: {self.riddle_id}")
        if self.subdir:
            parts.append(f"SUBDIR: {self.subdir}")
        for idx, train_pair in enumerate(self.train):
            parts.append(f"TRAIN {idx}")
            parts.append(train_pair.fmt(colored=colored))
        for idx, test_pair in enumerate(self.test):
            parts.append(f"TEST {idx}")
            parts.append(test_pair.fmt(colored=colored, with_output=with_test_outputs))
        return PAIR_GAP_STR.join(parts)

    def as_np(self, with_solution=True):
        return (
            [board.as_np(with_solution=True) for board in self.train],
            [board.as_np(with_solution=with_solution) for board in self.test],
        )

    @property
    def test_inputs(self) -> list[Board]:
        return [t.input for t in self.test]


class TaskData(pydantic.BaseModel):
    topk: int = settings.default_topk


HintsAccessed = set


class EvalResult(pydantic.BaseModel):
    riddle: Riddle
    task_data: TaskData
    solution: RiddleSolution
    hints_accessed: HintsAccessed = HintsAccessed()

    @pydantic.validator("solution")
    def validate_solution(cls, v, values):
        riddle = values["riddle"]
        if len(v) != len(riddle.test):
            raise ValueError(
                f"Solution length must be equal to number of test pairs "
                f"({len(riddle.test)}), but got {len(v)=}"
            )
        for solution in v:
            task_data = values["task_data"]
            if len(solution) != task_data.topk:
                raise ValueError(
                    f"Solution length must be equal to topk ({task_data.topk}),"
                    f" but got {len(solution)=}"
                )
        return v


class EvalResultList(pydantic.BaseModel):
    task_data: TaskData
    eval_results: list[EvalResult]

    @pydantic.validator("eval_results")
    def validate_eval_results(cls, v, values):
        task_data = values["task_data"]
        for eval_result in v:
            if eval_result.task_data != task_data:
                raise ValueError(
                    f"EvalResult task_data must be equal to task_data,"
                    f" but got {eval_result.task_data=}"
                )
        return v

    @property
    def hints_accessed(self):
        return HintsAccessed(
            itt.chain.from_iterable(
                result.hints_accessed for result in self.eval_results
            )
        )
