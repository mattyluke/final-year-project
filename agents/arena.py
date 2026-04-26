# Agents will be compared here.

from mcts import run_worker
from game_engine import Board
from multiprocessing import Pool
import itertools
import time

EMPTY = 0
RED = 1
BLACK = 2
WINNERS = ['empty', 'red', 'black']

C_VALUES = [0.5, 1.0, 1.41, 2.0, 2.5]
TIME_LIMIT = 3.0
GAMES_PER_PAIR = 30
RESULTS_FILE = "tournament_results.txt"
ELO_FILE = "elo_ratings.txt"
CORES = 6
K = 40

def expected_score(rating_a, rating_b):
    return 1/(1 + 10 ** ((rating_b - rating_a)/ 400))

def update_elo(ratings, agent_a, agent_b, winner):
    elo_a = expected_score(ratings[agent_a], ratings[agent_b])
    elo_b = expected_score(ratings[agent_b], ratings[agent_a])

    if winner == agent_a:
        a, b = 1, 0
    elif winner == agent_b:
        a, b = 0, 1
    else:
        a, b = 0.5, 0.5
    
    ratings[agent_a] += K * (a - elo_a)
    ratings[agent_b] += K * (b - elo_b)

def play_game(c_red, c_black, pool, policy):
    board = Board()
    player = RED
    turn = 0

    for _ in range(50):
        c = c_red if player == RED else c_black
        state = board.save()

        results = pool.map(run_worker,
                           [(state, player, TIME_LIMIT, c, 0, policy)] * CORES)
        
        combined = {}
        for result, _ in results:
            for move, visits in result.items():
                combined[move] = combined.get(move, 0) + visits
        
        token_move = max(combined, key=combined.get) if combined else None
        if token_move is None:
            return EMPTY

        _, ti, DIR = token_move
        board.move_token(ti, DIR)

        if board.check_win(player):
            return player

        state = board.save()
        results = pool.map(run_worker,
                           [(state, player, TIME_LIMIT, c, 1, policy)] * CORES)
        combined = {}
        for result, _ in results:
            for move, visits in result.items():
                combined[move] = combined.get(move, 0) + visits
        
        disc_move = max(combined, key=combined.get) if combined else None
        if disc_move is None:
            return EMPTY
        _, di, coord = disc_move
        board.move_disc(di, coord)
        
        player = BLACK if player == RED else RED
        turn += 1
        print(f"... Finished turn {turn} ...")

    return EMPTY

def run_tournament():
    start = time.time()
    elo = {c: 1000.0 for c in C_VALUES}
    stats = {c: {'wins': 0, 'losses': 0, 'draws': 0, 'games': 0} for c in C_VALUES}
    pairs = list(itertools.combinations(C_VALUES, 2))

    with Pool(CORES) as pool:
        for idx, (c1, c2) in enumerate(pairs):
            print(f"\nGame {idx+1}/{len(pairs)}: c={c1} vs c={c2}")

            # 30 total games, swap after 15 for moving first vs moving second for fairness
            for _ in range(15):
                winner = play_game(c1, c2, pool, 'cluster')
                stats[c1]['games'] += 1
                stats[c2]['games'] += 1
                if winner == RED:
                    winner_c = c1
                    stats[c1]['wins'] += 1
                    stats[c2]['losses'] += 1
                elif winner == BLACK:
                    stats[c2]['wins'] += 1
                    stats[c1]['losses'] += 1
                    winner_c = c2
                else:
                    winner_c = None
                    stats[c1]['draws'] += 1
                    stats[c2]['draws'] += 1
                print(f"Winner of game is {WINNERS[winner]}")
                update_elo(elo, c1, c2, winner_c)
            for _ in range(15):
                winner = play_game(c2, c1, pool, 'cluster')
                stats[c2]['games'] += 1
                stats[c1]['games'] += 1
                if winner == RED:
                    stats[c2]['wins'] += 1
                    stats[c1]['losses'] += 1
                    winner_c = c2
                elif winner == BLACK:
                    stats[c1]['wins'] += 1
                    stats[c2]['losses'] += 1
                    winner_c = c1
                else:
                    winner_c = None
                    stats[c1]['draws'] += 1
                    stats[c2]['draws'] += 1
                print(f"Winner of game is {WINNERS[winner]}")
                update_elo(elo, c1, c2, winner_c)
        
            with open(RESULTS_FILE, 'a') as f:
                f.write(f"Matchup c={c1} vs c={c2}\n")
                f.write(f"Elo after matchup: c={c1} -> {elo[c1]:.1f}, c={c2} -> {elo[c2]:.1f}\n")
    
    end = time.time()
    
    with open(ELO_FILE, 'w') as f:
        f.write("FINAL ELO RATINGS\n")
        for c, rating in sorted(elo.items(), key = lambda x: x[1], reverse=True):
            f.write(f"{c}: {rating:.1f}\n")
        f.write("\nFULL STATS FOR EVERY C-VALUE\n")
        for c, stats in stats.items():
            f.write(f"C-VALUE: {c}, WINS: {stats['wins']}, LOSSES: {stats['losses']}, DRAWS: {stats['draws']}, GAMES: {stats['games']}\n")
        f.write(f"This tournament was completed in {(end-start)/3600} hours")

if __name__ == '__main__':
    run_tournament()