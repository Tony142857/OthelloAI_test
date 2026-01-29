from board import BLACK, WHITE

class Player:
    def __init__(self, color):
        self.color = color

    def get_move(self, board):
        raise NotImplementedError

class HumanPlayer(Player):
    def get_move(self, board):
        board.print_board()
        legal = board.get_legal_moves(self.color)
        print(f"Legal moves for {'Black' if self.color==BLACK else 'White'}: {legal}")
        move = None
        while move not in legal:
            try:
                raw = input("Enter move as 'x y': ")
                x, y = map(int, raw.strip().split())
                move = (x, y)
            except:
                print("Invalid input.")
        return move