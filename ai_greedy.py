from player import Player
from evaluate import full_eval

class GreedyAI(Player):
    def get_move(self, board):
        legal = board.get_legal_moves(self.color)
        if not legal:
            return None
        best_score = float('-inf')
        best_move = None
        for move in legal:
            temp_board = copy_board(board)
            temp_board.do_move(move, self.color)
            score = full_eval(temp_board, self.color)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

def copy_board(board):
    import copy
    new_b = copy.deepcopy(board)
    return new_b
