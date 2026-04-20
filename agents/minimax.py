from evaluation import evaluate
from game_engine import Board

EMPTY = 0
RED = 1
BLACK = 2
UR = 0
MR = 1
DR = 2
DL = 3
ML = 4
UL = 5
DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

def minimax(board, depth, player, maximising, phase=0):
    if depth == 0 or board.check_win(RED) or board.check_win(BLACK):
        return evaluate(board, player)
    if maximising:
        value = float('-inf')
        if phase == 0:
            for token_move in board.generate_token_moves(player):
                value = max(value, minimax(board, depth, player, maximising=True, phase = 1))
