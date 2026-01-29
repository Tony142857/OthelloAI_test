from board import Board, BLACK, WHITE
from player import HumanPlayer
from ai_greedy import GreedyAI
from ai_minimax import MiniMaxAI

def game_loop(player1_class, player2_class, depth1=3, depth2=3):
    board = Board()
    player1 = player1_class(BLACK) if player1_class != MiniMaxAI else MiniMaxAI(BLACK, depth1)
    player2 = player2_class(WHITE) if player2_class != MiniMaxAI else MiniMaxAI(WHITE, depth2)
    turn = 0
    cur_player = player1
    while not board.is_game_over():
        cur_player = player1 if turn % 2 == 0 else player2
        color = cur_player.color
        move = cur_player.get_move(board)
        if move is not None:
            board.do_move(move, color)
        turn += 1
    b, w = board.count()
    board.print_board()
    print("Game Over.\nBlack: %d  White: %d" % (b, w))
    if b > w:
        print("Black wins!")
        return 1
    elif w > b:
        print("White wins!")
        return -1
    else:
        print("Draw.")
        return 0

if __name__ == '__main__':
    from ui import print_welcome
    print_welcome()
    print("1. Human vs GreedyAI\n2. Human vs MiniMaxAI\n3. GreedyAI vs MiniMaxAI")
    mode = input("Select mode: ")
    if mode == "1":
        game_loop(HumanPlayer, GreedyAI)
    elif mode == "2":
        game_loop(HumanPlayer, MiniMaxAI)
    elif mode == "3":
        game_loop(GreedyAI, MiniMaxAI)
    else:
        print("Invalid mode.")