import numpy as np

EMPTY, BLACK, WHITE = 0, 1, -1

DIRECTIONS = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

class Board:
    def __init__(self):
        self.size = 8
        self.board = np.zeros((self.size, self.size), dtype=int)
        self._init_board()

    def _init_board(self):
        mid = self.size // 2
        self.board[mid-1][mid-1] = WHITE
        self.board[mid][mid] = WHITE
        self.board[mid-1][mid] = BLACK
        self.board[mid][mid-1] = BLACK

    def in_board(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def get_legal_moves(self, color):
        legal = set()
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != EMPTY:
                    continue
                for dx, dy in DIRECTIONS:
                    x, y = i+dx, j+dy
                    found_opponent = False
                    while self.in_board(x, y) and self.board[x][y] == -color:
                        found_opponent = True
                        x, y = x+dx, y+dy
                    if found_opponent and self.in_board(x, y) and self.board[x][y] == color:
                        legal.add((i, j))
                        break
        return list(legal)

    def do_move(self, move, color):
        if move is None or move not in self.get_legal_moves(color):
            return False
        x0, y0 = move
        self.board[x0][y0] = color
        for dx, dy in DIRECTIONS:
            x, y = x0+dx, y0+dy
            to_flip = []
            while self.in_board(x, y) and self.board[x][y] == -color:
                to_flip.append((x, y))
                x += dx
                y += dy
            if to_flip and self.in_board(x, y) and self.board[x][y] == color:
                for fx, fy in to_flip:
                    self.board[fx][fy] = color
        return True

    def is_game_over(self):
        return not self.get_legal_moves(BLACK) and not self.get_legal_moves(WHITE)

    def count(self):
        black = np.sum(self.board == BLACK)
        white = np.sum(self.board == WHITE)
        return black, white

    def print_board(self):
        print("  " + " ".join(str(y) for y in range(self.size)))
        for x in range(self.size):
            line = []
            for y in range(self.size):
                v = self.board[x][y]
                if v == BLACK:
                    line.append('●')
                elif v == WHITE:
                    line.append('○')
                else:
                    line.append('.')
            print(f"{x} {' '.join(line)}")