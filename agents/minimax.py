from evaluation import evaluate_token, evaluate_disc_move
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



def minimax(board, depth, alpha, beta, player, maximising, phase=0):
    opponent = BLACK if player == RED else RED

    if board.check_win(RED):
        return (1000000 if player == RED else -1000000), None
    
    if board.check_win(BLACK):
        return (1000000 if player == BLACK else -1000000), None
    
    if depth == 0:
        return 0, None
    
    if phase == 0:
        moves = board.generate_token_moves(player)

        if not moves:
            return 0, None
        
        best_move = None

        if maximising:
            best_score = float('-inf')
            for move in moves:
                _, i, DIR = move
                move_score = evaluate_token(board, i, DIR, player)
                reverse = board.move_token(i, DIR)
                if reverse is False:
                    continue

                future_score, _ = minimax(board, depth, alpha, beta, player, 1, True)

                board.undo_token_move(*reverse)

                total_score = move_score + future_score

                if total_score > best_score:
                    best_score = total_score
                    best_move = move
                
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            
            return best_score, best_move
        else:
            best_score = float('inf')

            for move in moves:
                _, i, DIR = move
                move_score = evaluate_token(board, i, DIR, player)

                reverse = board.move_token(i, DIR)
                if reverse is False:
                    continue

                future_score, _ = minimax(board, depth, alpha, beta, player, 1, False)

                board.undo_token_move(*reverse)

                total_score = move_score + future_score

                if total_score < best_score:
                    best_score = total_score
                    best_move = move
                
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            
            return best_score, best_move
    else:
        moves = board.generate_disc_moves()
        if not moves:
            return 0, None
        
        best_move = None

        if maximising:
            best_score = float('-inf')

            for move in moves:
                _, i, coord = move

                move_score = evaluate_disc_move(board, i, coord, player)

                reverse = board.move_disc(i, coord)

                future_score, _ = minimax(board, depth - 1, alpha, beta, opponent, 0, False)

                board.undo_disc_move(*reverse)

                total_score = move_score + future_score

                if total_score > best_score:
                    best_score = total_score
                    best_move = move
                
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            
            return best_score, best_move
        else:
            best_score = float('inf')

            for move in moves:
                _, i, coord = move
                move_score = evaluate_disc_move(board, i, coord, player)
                reverse = board.move_disc(i, coord)

                future_score, _ = minimax(board, depth - 1, alpha, beta, opponent, 0, True)

                board.undo_disc_move(*reverse)

                total_score = move_score + future_score

                if total_score < best_score:
                    best_score = total_score
                    best_move = move
                
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            
            return best_score, best_move
        
if __name__ == "__main__":
    board = Board()
    score, best_move = minimax(board=board, depth=2, alpha=float('-inf'), beta=float('inf'), player=RED, phase = 0, maximising=True)

    print("Best score:",score)
    print("Best move:", best_move)