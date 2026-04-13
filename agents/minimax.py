from game_engine import Board
from evaluation import cluster_score
from copy import deepcopy
import time

def minimax(board, depth, maximizing_player, player, alpha = float('-inf'), beta = float('inf')):
    opponent = 'B' if player == 'R' else 'R'

    win, winner = board.check_win()

    if win:
        if winner == player:
            return float('inf'), None
        else:
            return float('-inf'), None
        
    if depth == 0:
        return cluster_score(board, player), None
    
    if maximizing_player:
        best_value = float('-inf')
        best_move = None

        for move in board.get_all_filtered_moves(player):
            snapshot = board.piece_map.copy()
            board.apply_move(board, move, player)
            value, _ = minimax(board, depth - 1, False, player, alpha, beta)
            board.piece_map = snapshot

            if value > best_value:
                best_value = value
                best_move = move
            
            alpha = max(alpha, best_value)

            if beta <= alpha:
                break

        return best_value, best_move
    
    else:
        best_value = float('inf')
        best_move = None

        for move in board.get_all_filtered_moves(opponent):
            snapshot = board.piece_map.copy()
            board.apply_move(board, move, opponent)
            value, _ = minimax(board, depth - 1, True, player, alpha, beta)
            board.piece_map = snapshot

            if value < best_value:
                best_value = value
                best_move = move

            beta = min(beta, best_value)

            if beta <= alpha:
                break

        return best_value, best_move
    
board = Board()
board.create_board()

player = 'R'
depth = 3

start = time.time()

best_score, best_move = minimax(board, depth, True, player)

end = time.time()

print(f"Best score: {best_score}")
print(f"Best move: {best_move}")

print(end - start)