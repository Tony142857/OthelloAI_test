import numpy as np
from board import BLACK, WHITE

corner_weight = 25
action_weight = 8
piece_weight = 1

CORNER_POS = [(0,0),(0,7),(7,0),(7,7)]

def base_eval(board: 'Board', color):
    opp = -color
    my_count = np.sum(board.board == color)
    opp_count = np.sum(board.board == opp)
    return piece_weight * (my_count - opp_count)

def mobility_eval(board: 'Board', color):
    opp = -color
    my_move = len(board.get_legal_moves(color))
    opp_move = len(board.get_legal_moves(opp))
    return action_weight * (my_move - opp_move)

def corner_eval(board: 'Board', color):
    opp = -color
    my_corner = sum(board.board[x][y]==color for x,y in CORNER_POS)
    opp_corner = sum(board.board[x][y]==opp for x,y in CORNER_POS)
    return corner_weight * (my_corner - opp_corner)

def full_eval(board: 'Board', color):
    return (base_eval(board, color) +
            mobility_eval(board, color) +
            corner_eval(board, color))