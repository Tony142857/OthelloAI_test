from board import Board, BLACK, WHITE

def print_welcome():
    print("==============================")
    print("         黑白棋 Othello        ")
    print("==============================")
    print("坐标输入格式: 行 列  (例: 2 3)")
    print("黑子：●   白子：○  空位：.")
    print("==============================\n")

def print_turn(board, color):
    print(f"\n现在是{'黑' if color == BLACK else '白'}方回合：")
    board.print_board()