from enum import Enum
import numpy as np
from arc.interface import BoardPair, Board

class Direction(Enum):
    horizontal = 1
    vertical = 2
    both = 3

def noop(o):
    return o

def cropInputAndOutput(inputPair:BoardPair, cols_to_rem_choice,rows_to_rem_choice,dir_choice_col,dir_choice_row)->BoardPair:
    input_np_board = inputPair.input.np
    output_np_board = inputPair.output.np
    input_np_board = cropBoard(input_np_board,cols_to_rem_choice,rows_to_rem_choice,dir_choice_col,dir_choice_row).np
    output_np_board = cropBoard(output_np_board,cols_to_rem_choice,rows_to_rem_choice,dir_choice_col,dir_choice_row).np

    return BoardPair(input=input_np_board.tolist(),output=output_np_board.tolist())

def cropBoard(boardIn:Board,cols_to_rem_choice,rows_to_rem_choice,dir_choice_col,dir_choice_row)->Board:
    if cols_to_rem_choice > 0 : 
        if dir_choice_col == -1:
            boardIn = boardIn[cols_to_rem_choice:,:]
        else:
            boardIn = boardIn[:-cols_to_rem_choice,:]
    if rows_to_rem_choice > 0:
        if dir_choice_row == -1:
            boardIn = boardIn[:,rows_to_rem_choice:]
        else:
            boardIn = boardIn[:,:-rows_to_rem_choice]

    return Board(__root__ = boardIn.tolist())

def doubleBoard(boardIn:Board,separation:int,is_horizontal_cat:bool,z_index_of_original:bool=0)->Board:
    """
    This function takes a Board and returns a new Board with the input board doubled.
    If is_horizontal_cat is True, the board is horizontally concatenated otherwise concatenation is vertical.
    Separation is the number of pixels between the two boards.
    This function supports negative separation values. In this case, one board is cropped to accomodate the other.
    if separation is negative, the z_index_of_original is used to determine which board lays ontop of the other.
    """

    np_board = boardIn.np
    ret_board_size = [len(np_board),len(np_board[0])]
    if is_horizontal_cat:
        ret_board_size[1] = ret_board_size[1]*2 + separation
    else:
        ret_board_size[0] = ret_board_size[0]*2 + separation
    ret_board = np.zeros(ret_board_size)

    if is_horizontal_cat:
        if z_index_of_original == 0:
            ret_board[:,:len(np_board[0])] = np_board
            ret_board[:,-len(np_board[0]):] = np_board
        else:
            ret_board[:,-len(np_board[0]):] = np_board
            ret_board[:,:len(np_board[0])] = np_board

    else:
        if z_index_of_original == 0:
            ret_board[:len(np_board),:] = np_board
            ret_board[-len(np_board):,:] = np_board
        else:
            ret_board[-len(np_board):,:] = np_board
            ret_board[:len(np_board),:] = np_board

    return Board(__root__ = ret_board.tolist())

def doubleInputBoard(board_pair:BoardPair,separation:int,is_horizontal_cat:bool,z_index_of_original:bool=0)->BoardPair:
    board_pair.input = doubleBoard(board_pair.input,separation,is_horizontal_cat,z_index_of_original)
    return board_pair

def rotate(board_pair:BoardPair, num_rotations:int=0) -> BoardPair:
    '''
    This function takes a Board and returns a new Board that is rotated 90 degrees `num_rotations` times
    '''
    assert num_rotations >= 0 and num_rotations < 4
    if num_rotations == 0:
        return board_pair
    return BoardPair(
        input=Board(__root__= np.rot90(board_pair.input.np, num_rotations)),
        output=Board(__root__= np.rot90(board_pair.output.np, num_rotations))
    )
    
    
    
def reflect(board_pair:BoardPair, x_axis:bool=False, y_axis:bool=False) -> BoardPair:
    '''
    This function takes a Board and returns a new Board that is reflected over one of the following: x-axis,y-axis, xy-axes, no axes
    '''
    x_axis,y_axis = int(x_axis),int(y_axis)
    
    if not x_axis and not y_axis:
        return board_pair.copy()
    
    if x_axis and y_axis:
        flip = None # None flips both axes
    elif x_axis:
        flip = 0
    elif y_axis:
        flip = 1
    
    return BoardPair(
        input=Board(__root__= np.flip(board_pair.input.np, flip)),
        output=Board(__root__= np.flip(board_pair.output.np, flip))
    )
def padInputOutput(board:BoardPair,size:int,pad_value:int)->BoardPair:
    input_np_board = board.input.np
    output_np_board = board.output.np
    input_np_board = padBoard(input_np_board,size,pad_value)
    output_np_board = padBoard(output_np_board,size,pad_value)
    return BoardPair(input=input_np_board.tolist(),output=output_np_board.tolist())

def padInputOnly(board:BoardPair,size:int,pad_value:int)->BoardPair:
    input_np_board = board.input.np
    input_np_board = padBoard(input_np_board,size,pad_value)
    return BoardPair(input=input_np_board.tolist(),output=board.output)    

def padBoard(boardIn:np.ndarray,size:int,pad_value:int)->np.ndarray:
    boardIn = np.pad(boardIn,((size,size),(size,size)),constant_values = pad_value)
    return boardIn

def superResolution(bp:BoardPair,factor:int,stretch_axis:Direction)-> BoardPair:
    bp.input = superResolutionBoard(bp.input,factor,stretch_axis)
    # bp.output = superResolutionBoard(bp.output,factor,stretch_axis)
    return bp

def superResolutionBoard(boardIn:Board,factor:int,stretch_axis:Direction)->Board:
    """
    This function takes a Board and returns a new Board that is super-resolved.
    The super-resolution is done by stretching the board in the specified direction.
    """
    np_board = boardIn.np
    if stretch_axis == Direction.horizontal:
        np_board = np.repeat(np_board,factor,axis=1)
    elif stretch_axis == Direction.vertical:
        np_board = np.repeat(np_board,factor,axis=0)
    elif stretch_axis == Direction.both:
        np_board = np.repeat(np_board,factor,axis=0)
        np_board = np.repeat(np_board,factor,axis=1)
    return Board(__root__ = np_board.tolist())