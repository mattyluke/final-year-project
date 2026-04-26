# Monte-Carlo tree search
import math
import random
import time
from game_engine import Board
import cProfile
import pstats
import sys
from multiprocessing import Pool
import numpy as np

EMPTY = 0
RED = 1
BLACK = 2
DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

global_iterations = 0

class Node:
    def __init__(self, player, phase, parent=None, move=None):
        self.player = player
        self.phase = phase
        self.parent = parent
        self.move = move
        self.reverse = None
        self.children = []
        self.untried_moves = None
        self.visits = 0
        self.value = 0

def chebyshev_distance(a, b):
    # Chebyshev distance returns the max distance on some axis between points a and b
    q1, r1 = a
    q2, r2 = b
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

def cohesion_score(board, player):
    opponent = BLACK if player == RED else RED

    def score_for(player):
        position_idx = board.red_i if player == RED else board.black_i
        positions = [board.coords[i] for i in position_idx]
        a, b, c = positions
        aq, ar = a
        bq, br = b
        cq, cr = c

        ab = (bq-aq, br-ar) in DIRECTIONS
        bc = (cq-bq, cr-br) in DIRECTIONS
        ac = (cq-aq, cr-ar) in DIRECTIONS

        adjacent_pairs = sum([ab, bc, ac])

        if adjacent_pairs >= 2:
            return float(100000000)

        distance_score = -(
            chebyshev_distance(a, b) +
            chebyshev_distance(b, c) +
            chebyshev_distance(a, c)
        )

        return adjacent_pairs * 10 + distance_score
    
    return score_for(player) - score_for(opponent)

def softmax(scores):
    exps = np.exp(scores - np.max(scores))
    return exps / exps.sum()

def biased_move_selection(board, moves, player, move_type):
    scores = []

    for move in moves:
        if move_type == 0:
            _, i, DIR = move
            reverse = board.move_token(i, DIR)
            score = cohesion_score(board, player)
            old_i, new_i, new_movable, was_movable = reverse
            board.undo_token_move(old_i, new_i, new_movable, was_movable)
        else:
            return random.choice(moves)
        
        scores.append(score)

    probabilities = softmax(scores)
    return random.choices(moves, weights=probabilities, k=1)[0]
    
def biased_move_simulation(board, player, phase):
    history = []
    current_player = player
    current_phase = phase
    winner = EMPTY

    for _ in range(50):
        if current_phase == 0:
            moves = board.generate_token_moves(current_player)
            if not moves:
                break
            move = biased_move_selection(board, moves, current_player, current_phase)
            _, i, DIR = move
            reverse = board.move_token(i, DIR)
            history.append((0, reverse))
            current_phase = 1
            if board.check_win(current_player):
                winner = current_player
                break
        else:
            move = board.random_disc_move()
            if not move:
                break
            i, coord = move
            reverse = board.move_disc(i, coord)
            history.append((1, reverse))
            current_phase = 0
            current_player = BLACK if current_player == RED else RED
    
    for phase, reverse in reversed(history):
        if phase == 1:
            i, old_coord, prev = reverse
            board.undo_disc_move(i, old_coord, prev)
        else:
            old_i, new_i, new_movable, was_movable = reverse
            board.undo_token_move(old_i, new_i, new_movable, was_movable)
    
    return winner

def expansion(node, board):
    move = random.choice(node.untried_moves)
    node.untried_moves.remove(move)

    if node.phase == 0:
        _, i, DIR = move
        reverse = board.move_token(i, DIR)
        next_phase = 1
        next_player = node.player
    else:
        _, i, coord = move
        reverse = board.move_disc(i, coord)
        next_phase = 0
        next_player = BLACK if node.player == RED else RED

    child = Node(next_player, next_phase, parent=node, move=move)
    child.reverse = reverse
    node.children.append(child)
    return child

def simulation(board, player, phase):
    history = []
    current_player = player
    current_phase = phase
    winner = EMPTY

    for _ in range(50):
        if current_phase == 0:
            move = board.random_token_move(current_player)
            if not move:
                break
            i, DIR = move
            reverse = board.move_token(i, DIR)
            history.append((0, reverse))
            current_phase = 1
            if board.check_win(current_player):
                winner = current_player
                break
        else:
            move = board.random_disc_move()
            if not move:
                break
            i, coord = move
            reverse = board.move_disc(i, coord)
            history.append((1, reverse))
            current_phase = 0
            current_player = BLACK if current_player == RED else RED
    
    for phase, reverse in reversed(history):
        if phase == 1:
            i, old_coord, prev = reverse
            board.undo_disc_move(i, old_coord, prev)
        else:
            old_i, new_i, new_movable, was_movable = reverse
            board.undo_token_move(old_i, new_i, new_movable, was_movable)
    
    return winner

def backpropagation(node, winner, root_player):
    while node is not None:
        node.visits += 1
        if winner == root_player:
            node.value += 1
        elif winner != EMPTY:
            node.value -= 1
        node = node.parent

def unwind(node, board):
    while node.parent is not None:
        if node.parent.phase == 0:
            old_i, new_i, new_movable, was_movable = node.reverse
            board.undo_token_move(old_i, new_i, new_movable, was_movable)
        else:
            i, old_coord, prev = node.reverse
            board.undo_disc_move(i, old_coord, prev)
        node.reverse=None
        node = node.parent

def get_immediate_win(board, player):
    moves = board.generate_token_moves(player)
    for move in moves:
        _, i, DIR = move
        reverse = board.move_token(i, DIR)
        won = board.check_win(player)
        old_i, new_i, new_movable, was_movable = reverse
        board.undo_token_move(old_i, new_i, new_movable, was_movable)
        if won:
            return move
    return None

def run_worker(args):
    board_state, player, time_limit, c, phase, policy = args

    board = Board()
    board.restore(board_state)

    if phase == 0:
        win_move = get_immediate_win(board, player)
        if win_move:
            return {win_move: 999999}, 0

    def ucb1_c(node):
        if node.visits == 0 or node.parent.visits == 0:
            return float('inf')
        return (node.value / node.visits) + c * math.sqrt(math.log(node.parent.visits) / node.visits)
    
    root = Node(player, phase = phase)
    if phase == 0:
        root.untried_moves = board.generate_token_moves(player)
    else:
        root.untried_moves = board.generate_disc_moves()
    deadline = time.time() + time_limit
    iterations = 0

    while time.time() < deadline:
        node = root

        while node.children and node.untried_moves == []:
            node = max(node.children, key=ucb1_c)
            if node.parent.phase == 0:
                _, i, DIR = node.move
                node.reverse = board.move_token(i, DIR)
            else:
                _, i, coord = node.move
                node.reverse = board.move_disc(i, coord)
        
        if node.untried_moves is None:
            if node.phase == 0:
                node.untried_moves = board.generate_token_moves(node.player)
            else:
                node.untried_moves = board.generate_disc_moves()
        
        if node.untried_moves:
            node = expansion(node, board)
        
        if policy == 'cluster':
            winner = biased_move_simulation(board, node.player, node.phase)
        else:
            winner = simulation(board, node.player, node.phase)
        backpropagation(node, winner, player)
        unwind(node, board)
        iterations += 1

    return {child.move: child.visits for child in root.children}, iterations

if __name__ == "__main__":
    board = Board()
    moves = board.generate_token_moves(BLACK)
    print(biased_move_selection(board, moves, BLACK, 0))