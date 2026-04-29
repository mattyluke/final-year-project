import math
import random
import time
from multiprocessing import Pool
from game_engine import Board
from mcts import run_worker
from minimax import minimax

EMPTY = 0
RED = 1
BLACK = 2
CORES = 6
TIME_LIMIT = 1.0  # 1s per phase, 2s per full turn
GAMES_PER_MATCHUP = 60
DEPTH = 2

def mcts_move(board, player, phase, policy, c):
    state = board.save()
    with Pool(CORES) as pool:
        results = pool.map(
            run_worker,
            [(state, player, TIME_LIMIT, c, phase, policy)] * CORES
        )
    combined = {}
    for result, _ in results:
        for move, visits in result.items():
            combined[move] = combined.get(move, 0) + visits
    if not combined:
        return None
    return max(combined, key=combined.get)

def minimax_move(board, player, phase):
    _, move = minimax(
        board=board,
        depth=DEPTH,
        alpha=float('-inf'),
        beta=float('inf'),
        player=player,
        phase=phase,
        maximising=True
    )
    return move

def apply_move(board, move, phase):
    if phase == 0:
        _, i, DIR = move
        board.move_token(i, DIR)
        return 1
    else:
        _, i, coord = move
        board.move_disc(i, coord)
        return 0

def play_game(red_agent, black_agent, red_c=2.5, black_c=2.5):
    board = Board()
    current_player = RED
    phase = 0

    for _ in range(200):
        if board.check_win(RED):
            return RED
        if board.check_win(BLACK):
            return BLACK

        agent = red_agent if current_player == RED else black_agent
        c = red_c if current_player == RED else black_c

        if agent == 'unbiased':
            move = mcts_move(board, current_player, phase, 'random', c)
        elif agent == 'biased':
            move = mcts_move(board, current_player, phase, 'cluster', c)
        elif agent == 'minimax':
            move = minimax_move(board, current_player, phase)

        if move is None:
            return EMPTY

        next_phase = apply_move(board, move, phase)

        if phase == 0:
            phase = 1
        else:
            phase = 0
            current_player = BLACK if current_player == RED else RED

    return EMPTY

def play_matchup(agent_a, agent_b, games, c_a=2.5, c_b=2.5):
    wins_a = 0
    wins_b = 0
    draws = 0
    half = games // 2

    print(f"  {agent_a} (RED) vs {agent_b} (BLACK) - {half} games...")
    for i in range(half):
        winner = play_game(agent_a, agent_b, red_c=c_a, black_c=c_b)
        if winner == RED:
            wins_a += 1
        elif winner == BLACK:
            wins_b += 1
        else:
            draws += 1
        print(f"    Game {i+1}/{half} done")

    print(f"  {agent_b} (RED) vs {agent_a} (BLACK) - {half} games...")
    for i in range(half):
        winner = play_game(agent_b, agent_a, red_c=c_b, black_c=c_a)
        if winner == RED:
            wins_b += 1
        elif winner == BLACK:
            wins_a += 1
        else:
            draws += 1
        print(f"    Game {i+1}/{half} done")

    return wins_a, wins_b, draws

if __name__ == "__main__":
    agents = ['unbiased', 'biased', 'minimax']
    c_values = {'unbiased': 2.5, 'biased': 4.0, 'minimax': None}

    total_wins = {a: 0 for a in agents}
    total_games = {a: 0 for a in agents}

    matchups = [
        ('unbiased', 'biased'),
        ('unbiased', 'minimax'),
        ('biased', 'minimax'),
    ]

    print("=" * 50)
    print("ROUND ROBIN TOURNAMENT")
    print("=" * 50)

    for agent_a, agent_b in matchups:
        print(f"\n{agent_a.upper()} vs {agent_b.upper()}")
        c_a = c_values[agent_a]
        c_b = c_values[agent_b]

        wins_a, wins_b, draws = play_matchup(
            agent_a, agent_b, GAMES_PER_MATCHUP, c_a, c_b
        )

        total_wins[agent_a] += wins_a
        total_wins[agent_b] += wins_b
        total_games[agent_a] += GAMES_PER_MATCHUP
        total_games[agent_b] += GAMES_PER_MATCHUP

        print(f"  Result: {agent_a}={wins_a} {agent_b}={wins_b} draws={draws}")

    print("\n" + "=" * 50)
    print("FINAL WIN RATES")
    print("=" * 50)
    for agent in agents:
        rate = (total_wins[agent] / total_games[agent]) * 100
        print(f"{agent}: {total_wins[agent]}/{total_games[agent]} = {rate:.1f}%")