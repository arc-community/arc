#!/usr/bin/env python3

import itertools as itt
from typing import Optional, Callable
from functools import reduce, partial

import numpy as np
import pydantic
from colored import attr, bg, fg
from matplotlib import pyplot as plt

from arc.settings import settings

CELL_PADDING_STR = " " * settings.cell_padding
BOARD_GAP_STR = " " * settings.board_gap
PAIR_GAP_STR = "\n" + " " * settings.pair_gap + "\n"

COLORMAP = {0: 0, 1: 4, 2: 1, 3: 2, 4: 3, 5: 8, 6: 5, 7: 166, 8: 6, 9: 52}


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
        color = COLORMAP[value]
        value_str = f"{CELL_PADDING_STR}{value}{CELL_PADDING_STR}"
        if colored:
            return f"{fg(15)}{bg(color)}{value_str}{attr(0)}"
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
    original: Optional['BoardPair'] = None
    default_augment_funcs: Optional[list[Callable]] = None

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
    
    def augment(self, augment_funcs: list[Callable]=None, with_solution: bool=True) -> 'BoardPair':
        if not augment_funcs and not self.default_augment_funcs:
            raise ValueError(f"No augmentation functions found. Pass augment_funcs to augment method or set default_augment_funcs")
        augment_funcs = augment_funcs if augment_funcs else self.default_augment_funcs
        augment_funcs = [func() for func in augment_funcs]
        augmenter = partial(reduce, lambda acc,f: f(acc), augment_funcs)
        return self._augment(augmenter,with_solution)
    
    def _augment(self, augmenter: Callable, with_solution: bool) -> 'BoardPair':
        this = self if self.original is None else self.original
        input = augmenter(this.input.data)
        output = augmenter(this.output.data) if with_solution else None
        return BoardPair(input=input, output=output, original=this, default_augment_funcs=self.default_augment_funcs)


class Riddle(pydantic.BaseModel):
    train: list[BoardPair]
    test: list[BoardPair]
    riddle_id: Optional[str] = None
    subdir: Optional[str] = None
    original: Optional['Riddle'] = None
    default_augment_funcs: Optional[list[Callable]] = None

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

    def fmt_plt(self, with_test_outputs=False):
        parts = [pair.as_np() for pair in self.train]
        parts.extend(pair.as_np(with_solution=with_test_outputs) for pair in self.test)

        def _draw_board(board: Optional[np.ndarray], ax: plt.Axes):
            if board is None:
                ax.remove()
            else:
                ax.matshow(board, cmap="nipy_spectral", vmin=0.0, vmax=9.0)
                ax.xaxis.set_visible(False)
                ax.yaxis.set_visible(False)

        fig, axs = plt.subplots(len(parts), 2)
        for (inboard, outboard), (inax, outax) in zip(parts, axs):
            _draw_board(inboard, inax)
            _draw_board(outboard, outax)

        plt.tight_layout()
        return fig, axs

    def as_np(self, with_solution=True):
        return (
            [board.as_np(with_solution=True) for board in self.train],
            [board.as_np(with_solution=with_solution) for board in self.test],
        )
    
    def augment(self, augment_funcs: list[Callable]=None, with_solution=True) -> 'Riddle':
        if not augment_funcs and not self.default_augment_funcs:
            raise ValueError(f"No augmentation functions found. Pass augment_funcs to augment method or set default_augment_funcs")
        augment_funcs = augment_funcs if augment_funcs else self.default_augment_funcs
        augment_funcs = [func() for func in augment_funcs]
        augmenter = partial(reduce, lambda acc,f: f(acc), augment_funcs)
        return self._augment(augmenter, with_solution) 
    
    def _augment(self, augmenter, with_solution) -> 'Riddle':
        this = self if self.original is None else self.original
        train = [board._augment(with_solution=True, augmenter=augmenter) for board in this.train]
        test = [board._augment(with_solution=with_solution, augmenter=augmenter) for board in this.test]
        return Riddle(
            train=train, 
            test=test, 
            riddle_id=self.riddle_id,
            subdir=self.subdir,
            original=this, 
            default_augment_funcs=self.default_augment_funcs, 
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
