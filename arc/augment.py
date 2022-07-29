#!/usr/bin/env python3

import random
from typing import Optional, Callable

from arc.interface import Riddle, BoardPair, Board


def noop(board: Board = None) -> Board: 
    return board


def random_rotation_seed(choice:int = None) -> Callable:

    def rotate_90_degrees(board: Board) -> list[list[int]]: 
        return [list(x) for x in zip(*reversed(board.data))]
    
    def rotate_180_degrees(board: Board) -> list[list[int]]:
        return [list(reversed(x)) for x in reversed(board.data)]
    
    def rotate_270_degrees(board: Board) -> list[list[int]]:
        return list(reversed([list(x) for x in zip(*board.data)]))

    rotation_funcs = [noop, rotate_90_degrees, rotate_180_degrees, rotate_270_degrees]
    func = random.choice(rotation_funcs) if choice is None else rotation_funcs[choice]

    def random_rotation(board: Board) -> list[list[int]]: 
        return func(board)
    
    return random_rotation


def random_reflect_seed(choice:int = None) -> Callable:
    
    def reflect_x_axis(board: Board) -> list[list[int]]:  
        return list(reversed(board))

    def reflect_y_axis(board: Board) -> list[list[int]]: 
        return [list(reversed(x)) for x in board]
    
    reflect_funcs = [reflect_x_axis, reflect_y_axis, noop]
    func = random.choice(reflect_funcs) if choice is None else reflect_funcs
    
    def random_reflect(board: Board) -> list[list[int]]: 
        return func(board)

    return random_reflect


def random_recolor_seed(include0: bool = False) -> Callable:
    if include0:
        colours = random.sample(list(range(10)),10)
    else: 
        colours = [0] + random.sample(list(range(1,10)),9)

    def random_recolor(board: Board) -> list[list[int]]:
        return [[colours[o] for o in row] for row in board]

    return random_recolor