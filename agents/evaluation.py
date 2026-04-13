from game_engine import Board

# Function which returns a higher value if the maximising player has pieces close together, and opponents pieces are spaced apart.

def cluster_score(board, player):
    player_tokens = []
    opponent_tokens = []

    for coord, value in board.get_board().items():
        if value == 'N':
            continue
        if value == player:
            player_tokens.append(coord)
        else:
            opponent_tokens.append(coord)
    
    if not player_tokens or not opponent_tokens:
        return None
    
    player_x_avg = sum(c[0] for c in player_tokens)/len(player_tokens)
    player_y_avg = sum(c[1] for c in player_tokens)/len(player_tokens)
    player_z_avg = sum(c[2] for c in player_tokens)/len(player_tokens)

    opponent_x_avg = sum(c[0] for c in opponent_tokens)/len(opponent_tokens)
    opponent_y_avg = sum(c[1] for c in opponent_tokens)/len(opponent_tokens)
    opponent_z_avg = sum(c[2] for c in opponent_tokens)/len(opponent_tokens)

    player_total_dist = 0
    opponent_total_dist = 0

    for (x, y, z) in player_tokens:
        dx = abs(x - player_x_avg)
        dy = abs(y - player_y_avg)
        dz = abs(z - player_z_avg)

        player_total_dist += dx**2 + dy**2 + dz**2

    for (x, y, z) in opponent_tokens:
        dx = abs(x - opponent_x_avg)
        dy = abs(y - opponent_y_avg)
        dz = abs(z - opponent_z_avg)

        opponent_total_dist += dx**2 + dy**2 + dz**2
    
    return opponent_total_dist - player_total_dist

board = Board()
board.create_board()