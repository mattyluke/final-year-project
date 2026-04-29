from multiprocessing import Pool
from game_engine import Board
from mcts import run_worker

TIME_LIMIT = 1.0
RED = 1

def measure(cores, policy):
    board = Board()
    state = board.save()

    with Pool(cores) as pool:
        results = pool.map(
            run_worker,
            [(state, RED, TIME_LIMIT, 2.5, 0, policy)] * cores
        )

    total_iterations = sum(
        sum(result.values())
        for result, _ in results
    )

    return total_iterations

if __name__ == "__main__":
    print(f"{'Cores':<8} {'Unbiased':>12} {'Biased':>12}")
    print("-" * 34)

    for cores in range(1, 9):
        unbiased = measure(cores, 'random')
        biased = measure(cores, 'cluster')
        print(f"{cores:<8} {unbiased:>12} {biased:>12}")