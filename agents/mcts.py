# Monte-Carlo tree search
import math
import random
import time
from game_engine import Board
import cProfile
import pstats

EMPTY = 0
RED = 1
BLACK = 2

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


def ucb1(node, c=1.41):
    if node.visits == 0 or node.parent.visits == 0:
        return float('inf')
    return (node.value / node.visits) + c*(math.sqrt(math.log(node.parent.visits)/node.visits))


def selection(node, board):
    while node.children and node.untried_moves == []:
        node = max(node.children, key=lambda child: ucb1(child))
        if node.parent.phase == 0:
            _, i, DIR = node.move
            node.reverse = board.move_token(i, DIR)
        else:
            _, i, coord = node.move
            node.reverse = board.move_disc(i, coord)
    return node

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

    for _ in range(200):
        if current_phase == 0:
            moves = board.generate_token_moves(current_player)
            if not moves:
                break
            _, i, DIR = random.choice(moves)
            reverse = board.move_token(i, DIR)
            history.append((0, reverse))
            current_phase = 1
            if board.check_win(current_player):
                break

        else:
            moves = board.generate_disc_moves()
            if not moves:
                break
            _, i, coord = random.choice(moves)
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

def backpropagation(node, winner):
    while node is not None:
        node.visits += 1
        if winner == EMPTY:
            break
        if node.player == winner:
            node.value += 1
        else:
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

def mcts(board, player, iterations=20000):
    root = Node(player, phase=0)
    root.untried_moves = board.generate_token_moves(player)
    
    for _ in range(iterations):
        node = root

        node = selection(node, board)

        if node.untried_moves is None:
            if node.phase == 0:
                node.untried_moves = board.generate_token_moves(node.player)
            else:
                node.untried_moves = board.generate_disc_moves()

        if node.untried_moves:
            node = expansion(node, board)
        
        winner = simulation(board, node.player, node.phase)
        backpropagation(node, winner)
        unwind(node, board)

    best_child = max(root.children, key=lambda child: child.visits)
    return best_child.move

#board = Board()
#start = time.time()
#move = mcts(board, RED)
#end = time.time()
#print(end - start)

#cProfile.run('mcts(board, RED, iterations=1000)', sort='cumulative')