from player import Player
from evaluate import full_eval, base_eval
import copy

class MiniMaxAI(Player):
    def __init__(self, color, depth=3, eval_fn=full_eval):
        super().__init__(color)
        self.depth = depth
        self.eval_fn = eval_fn

    def get_move(self, board):
        legal = board.get_legal_moves(self.color)
        if not legal:
            return None
        best_move = legal[0]
        best_score = float('-inf')
        for move in legal:
            temp_board = copy.deepcopy(board)
            temp_board.do_move(move, self.color)
            score = self.minimax(temp_board, self.depth - 1, -self.color, float('-inf'), float('inf'))
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, board, depth, color, alpha, beta):
        if depth == 0 or board.is_game_over():
            return self.eval_fn(board, self.color)
        legal = board.get_legal_moves(color)
        if not legal:
            return self.minimax(board, depth-1, -color, alpha, beta)
        if color == self.color:  # max层
            value = float('-inf')
            for move in legal:
                temp_board = copy.deepcopy(board)
                temp_board.do_move(move, color)
                value = max(value, self.minimax(temp_board, depth-1, -color, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:  # min层
            value = float('inf')
            for move in legal:
                temp_board = copy.deepcopy(board)
                temp_board.do_move(move, color)
                value = min(value, self.minimax(temp_board, depth-1, -color, alpha, beta))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value