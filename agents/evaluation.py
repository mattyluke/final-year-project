from game_engine import Board

# Function which returns a higher value if the maximising player has pieces close together, and opponents pieces are spaced apart.

def hex_distance(ax, ay, bx, by):
    return max(abs(bx-ax), abs(by-ay), abs((bx-ax)-(by-ay)))

RED = 1
BLACK = 2
DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

def evaluate(board, player):
    def cohesion(pieces):
        a, b, c = pieces
        ax, ay = board.coords[a]
        bx, by = board.coords[b]
        cx, cy = board.coords[c]

        return (hex_distance(ax, ay, bx, by) +
                hex_distance(bx, by, cx, cy) +
                hex_distance(ax, ay, cx, cy))

    player_pieces = board.red_i if player == RED else board.black_i
    opponent_pieces = board.black_i if player == RED else board.red_i

    return cohesion(opponent_pieces) - cohesion(player_pieces)
