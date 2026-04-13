# Monte-Carlo Tree Search Approach

import math
import random
from game_engine import Board

class MCTSNode():
    def __init__(self, parent, move, player):
        self.parent = parent
        self.move = move
        self.player = player

        self.children = []
        self.visits = 0
        self.value = 0

        self.untried_moves= None

def switch_player(p):
    return 'b' if p == 'r' else 'r'

def rollout(board, player):
    current_player = player
    path = []

    while True:
        win_r = board.check_win('r')
        win_b = board.check_win('b')

        if win_r or win_b:
            for record in reversed(path):
                board.undo_move(record)
            return 'r' if win_r else 'b'
        
        moves = board.get_all_moves(current_player)

        if not moves:
            return switch_player(current_player)
        
        move = random.choice(moves)
        record = board.apply_move(move)

        current_player = switch_player(current_player)

def ucb1(node, c = 1.4):
    best_score = -float('inf')
    best = None

    for child in node.children:
        exploit = child.value / (child.visits + 1e-6)
        explore = c * math.sqrt(math.log(node.visits + 1) / (child.visits + 1e-6))
        score = exploit + explore

        if score > best_score:
            best_score = score
            best = child

    return best




def mcts(board, root_player, iterations=1000):
    root = MCTSNode(parent=None, move=None, player=root_player)

    for _ in range(iterations):
        node = root
        current_player = root_player

        path = []

        # Selection

        while node.untried_moves == [] and node.children:
            node = ucb1(node)

            record = board.apply_move(node.move)
            path.append(record)

            current_player  = switch_player(current_player)
        
        # Expansion

        if node.untried_moves is None:
            node.untried_moves = board.get_all_moves(current_player)
        else:
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)

            record = board.apply_move(move)
            path.append(record)

            child = MCTSNode(node, move, current_player)
            node.children.append(child)

            node = child
            current_player = switch_player(current_player)

        # Simulation

        winner = rollout(board, current_player)

        reward = 1 if winner == root_player else -1

        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent
            reward = -reward

        for record in reversed(path):
            board.undo_move(record)

    return max(root.children, key = lambda c: c.visits).move

board = Board()
board.create_board()

move = mcts(board, 'r', iterations=1000)

print('MCTS Move:',move)
record = board.apply_move(move)
print("Applied move:",move)