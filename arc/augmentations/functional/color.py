import numpy as np
from arc.interface import BoardPair

def permute_color(InputPair:BoardPair, color_permutation):
    input_np_board = InputPair.input.np
    output_np_board = InputPair.output.np

    ret_input_board = np.zeros_like(input_np_board)
    ret_output_board = np.zeros_like(output_np_board)
    for i in range(len(color_permutation)):
        ret_input_board[input_np_board==i] = color_permutation[i]
        ret_output_board[output_np_board==i] = color_permutation[i]
        
    return BoardPair(input = ret_input_board.tolist(),output = ret_output_board.tolist())