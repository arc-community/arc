#!/usr/bin/env python3

import numpy as np

from arc.agents import Agent
from arc.interface import BoardData, EvalResult, Riddle


def eval_solution_for_riddle(riddle: Riddle, solution: list[BoardData]) -> EvalResult:
    if len(solution) != len(riddle.test):
        raise ValueError(
            f"Expected {len(riddle.test)} solutions, but got {len(solution)}"
        )

    result = EvalResult(
        riddle=riddle,
        solution=solution,
        board_size_scores=[],
        board_content_scores=[],
    )
    for sol, test in zip(solution, riddle.test):
        sol_np = np.asarray(sol)
        test_np = test.output.np
        if sol_np.shape == test_np.shape:
            bss = 1.0
            bcs = np.mean(np.equal(sol_np, test_np))
        else:
            bss = 0.0
            bcs = 0.0
        result.board_size_scores.append(bss)
        result.board_content_scores.append(bcs)
    return result


def evaluate_agent_on_riddle(agent: Agent, riddle: Riddle) -> EvalResult:
    solution = agent.solve_riddle(riddle)
    return eval_solution_for_riddle(riddle=riddle, solution=solution)
