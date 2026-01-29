import time
from main import game_loop
from ai_greedy import GreedyAI
from ai_minimax import MiniMaxAI

def battle(ai1_class, ai2_class, n_games=10, depth1=3, depth2=3, verbose=True):
    result = {"ai1":0, "ai2":0, "draw":0}
    total_time = []
    for i in range(n_games):
        start = time.time()
        if verbose:
            print(f"\nGame {i+1} ...")
        winner = game_loop(ai1_class, ai2_class, depth1, depth2)
        end = time.time()
        total_time.append(end-start)
        if winner == 1:
            result["ai1"] += 1
        elif winner == -1:
            result["ai2"] += 1
        else:
            result["draw"] += 1
    print(result)
    print(f"Avg time/game: {sum(total_time)/n_games:.2f}s")

if __name__ == "__main__":
    # 示例：MiniMaxAI(3) vs GreedyAI
    battle(MiniMaxAI, GreedyAI, n_games=5, depth1=3, depth2=0)