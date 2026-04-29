from game_engine import Board

EMPTY = 0
RED = 1
BLACK = 2
DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

def hex_distance(ax, ay, bx, by):
    return max(
        abs(bx - ax),
        abs(by - ay),
        abs((bx - ax) - (by - ay))
    )

def count_adjacent_pairs(board, pieces):
    coords = [board.coords[i] for i in pieces]
    a, b, c = coords
    pairs = 0
    if (b[0] - a[0], b[1] - a[1]) in DIRECTIONS:
        pairs += 1
    if(c[0]-b[0], c[1]-b[1]) in DIRECTIONS:
        pairs += 1
    if (c[0]-a[0], c[1]-a[1]) in DIRECTIONS:
        pairs += 1
    return pairs

def evaluate_token(board, i, DIR, player):
    player_pieces = board.red_i if player == RED else board.black_i
    opponent = BLACK if player == RED else RED

    our_pairs_before = count_adjacent_pairs(board, player_pieces)

    old_i, new_i, new_movable, was_movable = board.move_token(i, DIR)

    for move in board.generate_token_moves(opponent):
        o_i, n_i, n_m, w_m = board.move_token(move[1], move[2])

        won = board.check_win(opponent)
        board.undo_token_move(o_i, n_i, n_m, w_m)

        if won:
            board.undo_token_move(old_i, new_i, new_movable, was_movable)
            return -1000000

    if board.check_win(player):
        board.undo_token_move(old_i, new_i, new_movable, was_movable)
        return 100000

    score = 0

    our_pairs_after = count_adjacent_pairs(board, player_pieces)

    board.undo_token_move(old_i, new_i, new_movable, was_movable)

    score += (our_pairs_after - our_pairs_before) * 1000

    coords = [board.coords[p] for p in player_pieces]
    total_dist = 0
    for a in range(3):
        for b in range(a+1, 3):
            total_dist += hex_distance(*coords[a], *coords[b])
    
    score -= total_dist * 50

    score += len(board.generate_token_moves(player)) * 20
    score -= len(board.generate_token_moves(opponent)) * 20

    return score

def evaluate_disc(board, coord, player):
    opponent = BLACK if player == RED else RED
    score = 0

    axes = [(0, 3), (1, 4), (2, 5)]

    for d1, d2 in axes:
        left = None
        right = None

        x, y = coord
        dx, dy = DIRECTIONS[d1]
        while True:
            x += dx
            y += dy
            idx = board.index.get((x, y))
            if idx is None:
                break
            if board.board[idx] != EMPTY:
                left = board.board[idx]
                break
        
        x, y = coord
        dx, dy = DIRECTIONS[d2]
        while True:
            x += dx
            y += dy
            idx = board.index.get((x, y))
            if idx is None:
                break
            if board.board[idx] != EMPTY:
                right = board.board[idx]
                break
        
        if left == player and right == player:
            score += 100
        elif left == opponent and right == opponent:
            score -= 100
        elif left == player or right == player:
            score += 10
        elif left == opponent or right == opponent:
            score -= 10
    
    return score

def evaluate_disc_move(board, i, coord, player):
    old_coord = board.coords[i]
    removal_score = evaluate_disc(board, old_coord, player)
    placement_score = evaluate_disc(board, coord, player)

    return placement_score - removal_score