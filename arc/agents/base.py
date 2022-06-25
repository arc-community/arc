#!/usr/bin/env python3

from arc.interface import Board, BoardData, Riddle


class Agent:
    def __init__(self):
        pass

    def solve_riddle(self, riddle: Riddle) -> list[BoardData]:
        return [self.solve_test_sample(riddle, test.input) for test in riddle.test]

    def solve_test_sample(self, riddle: Riddle, test: Board) -> BoardData:
        raise NotImplementedError()
