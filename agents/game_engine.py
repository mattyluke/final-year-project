# Game Logic

# Every piece will be stored in a dict, {(coord): occupation, ...}
# Directions: {'ur': (1, 0, -1), 'mr': (1, -1, 0), 'dr': (0, -1, 1), 'dl': (-1, 0, 1), 'ml': (-1, 1, 0), 'ul': (0, 1, -1)}

import copy

DIRECTIONS = {'ur': (1, 0, -1), 'mr': (1, -1, 0), 'dr': (0, -1, 1), 'dl': (-1, 0, 1), 'ml': (-1, 1, 0), 'ul': (0, 1, -1)}

class Board:
    def __init__(self, piece_map=None):
        self.piece_map = {}
        self.just_moved_tuple = None
        if piece_map:
            self.piece_map = piece_map
    
    def get_board(self):
        return self.piece_map
    
    def get_just_moved(self):
        return self.just_moved_tuple

    def create_board(self):
        tuples = [(x, y, -(x+y))
                  for x in range(-2, 3)
                  for y in range(-2, 3)
                  if -2 <= -(x + y) <= 2]
        
        red_tuples = [(-2, 1, 1), (1, -2, 1), (1, 1, -2)]
        black_tuples = [(-1, 2, -1), (2, -1, -1), (-1, -1, 2)]

        for tuple in tuples:
            if tuple in red_tuples:
                self.piece_map[tuple] = 'R'
                continue
            elif tuple in black_tuples:
                self.piece_map[tuple] = 'B'
                continue
            else:
                self.piece_map[tuple] = 'N'

    def move_token(self, coord, direction, occupation):
        if self.piece_map[coord] != occupation:
            print(occupation)
            return False
        
        x, y, z = coord
        dx, dy, dz = DIRECTIONS[direction]

        # Condition check: Does the next piece exist, and is not occupied? If so then move.
        while True:
            next_coord = (x + dx, y + dy, z + dz)
            if next_coord not in self.piece_map:
                break

            if self.piece_map[next_coord] != 'N':
                break

            x, y, z = next_coord
        
        # If we try to move a player in some direction where the player cannot move any tiles, that is x, y and z are all unchanged after the action,
        # we need to return False, it is an illegal move.

        if coord == (x, y, z):
            return False

        self.piece_map[coord] = 'N'
        self.piece_map[(x,y,z)] = occupation

        return True
    
    def move_disc(self, original_loc, new_loc):
        if self.piece_map.get(original_loc) == None:
            return False
        if self.piece_map.get(new_loc) is not None:
            return False
        
        # When can we move a piece? If its number of neighbours < 5 and it is currently unoccupied.
        if self.piece_map[original_loc] != 'N':
            return False
        
        # Now check all directions, if the count ever reaches 5, return False, otherwise, continue
        count = 0
        x, y, z = original_loc
        for dx, dy, dz in DIRECTIONS.values():
            if self.piece_map.get((x+dx, y+dy, z+dz)) != None:
                count += 1
            if count >= 5:
                return False
            
        # Passed neighbour check, now we need to look at the new location, the constraint is must have at least two neighbours currently on the board, but no more than
        # four neighbours, so that the piece would be able to 'slide in' on a board.

        x2, y2, z2 = new_loc
        count = 0
        for dx, dy, dz in DIRECTIONS.values():
            if (x2+dx, y2+dy, z2+dz) == original_loc:
                continue
            if self.piece_map.get((x2+dx, y2+dy, z2+dz)) != None:
                count += 1
            if count >= 5:
                print(f"Piece to be moved: {original_loc} to {new_loc}")
                print(f"Current board: {self.piece_map}")
                print(f"Failing because count = {count}")
                return False
        if count < 2:
            return False
        
        # Now, all constraints have been verified, so it is a valid board move, and we can return True, and set the new location as the just moved piece
        self.piece_map[new_loc] = self.piece_map[original_loc]
        del self.piece_map[original_loc]
        self.just_moved_tuple = new_loc
        return True
    
    def check_win(self):
        # There should be some token which has neighbours = 2 if a win has been made.
        winner = None
        for coord, value in self.piece_map.items():
            if value == 'N':
                continue
            else:
                # Occupied, check neighbour count
                neighbour_count = 0
                x,y,z = coord
                for dx, dy, dz in DIRECTIONS.values():
                    (cx, cy, cz) = (x+dx, y+dy, z+dz)
                    if self.piece_map.get((cx, cy, cz)) is not None:
                        if self.piece_map[(cx, cy, cz)] == value:
                            neighbour_count += 1
                            if neighbour_count == 2:
                                winner = value
                                return True, winner
                        else:
                            continue
                    else:
                        continue
        return False, winner
    
    def get_token_moves(self, player):
        moves = []

        for coord, value in self.piece_map.items():
            if value != player:
                continue

            for direction in DIRECTIONS:
                test_board = Board(piece_map=self.piece_map.copy())

                if test_board.move_token(coord, direction, player):
                    moves.append((coord, direction))
        
        return moves
    
    # Disc movements gets exponentially large very quickly, so we need to strategically reduce the amount
    # of potential states we consider, so we can limit the options we consider with both phases of disc movement:
    # 1. When removing a disc, remove pieces which are in LOS of our opponent, don't remove pieces which are in LOS of our tokens
    # 2. When placing a disc, place it which are in LOS of our tokens, not where it is in LOS of our opponents tokens
    #
    # This should maximise our angles of attack, and minimise the opponents, and provide more opportunities for our pieces to cluser, and reduce theirs
    # We know if two pieces are on some axes, because they share some value in their coords i.e. (2, 0, -2) and (6, 0, -6) are on the same axes as they share 0 in y.
    
    def neighbour_count(self, coord, ignore_piece=None):
        piece_map = self.piece_map
        count = 0
        for offset in DIRECTIONS.values():
            (x, y, z) = coord
            x2 = x + offset[0]
            y2 = y + offset[1]
            z2 = z + offset[2]

            if (x2, y2, z2) == ignore_piece:
                continue
            if piece_map.get((x2, y2, z2)) is not None:
                count += 1
        return count

    def reachable_edges(self, player):
        # This returns the top 3 'reachable' pieces on the board for some player
        valid = {}
        piece_map = self.piece_map
            
        for (x,y,z), value in piece_map.items():
            if value == player:
                for offset in DIRECTIONS.values():
                    delta = 1
                    while True:
                        x2 = x + offset[0]*delta
                        y2 = y + offset[1]*delta
                        z2 = z + offset[2]*delta
                        tile = piece_map.get((x2, y2, z2))
                        if tile is None:
                            x2 = x + offset[0]*(delta - 1)
                            y2 = y + offset[1]*(delta - 1)
                            z2 = z + offset[2]*(delta - 1)
                            if piece_map.get((x2, y2, z2)) == 'N':
                                if self.neighbour_count((x2, y2, z2)) < 5:
                                    valid[(x2, y2, z2)] = valid.get((x2, y2, z2), 0) + 1
                            break
                        if tile == 'N':
                            delta += 1
                        else:
                            break
        return dict(sorted(valid.items(), key=lambda item: item[1], reverse=True)[:3])



    def get_disc_origins(self, filtered=False, player=None):
        if filtered and player in ('R', 'B'):
            opponent = 'R' if player == 'B' else 'B'
            return self.reachable_edges(opponent)

        valid = []
        piece_map = self.piece_map
        directions = DIRECTIONS.values()

        for (x,y,z), value in piece_map.items():
            if value != 'N':
                continue
            
            count = 0

            for dx, dy, dz in directions:
                if (x+dx, y+dy, z+dz) in piece_map:
                    count += 1
                    if count > 4:
                        break
            
            if count <= 4:
                valid.append((x, y, z))
        
        return valid

    # For potential new locations, we want to have the same thing as origins, but extend it so that we consider the first piece which does not exist, count the neighbours and append it
    # If it does not already exist, otherwise increase its value by 1, decrease by 1 if it helps the opponents

    def convergent_destinations(self, player, origin):
        # This returns the top 3 'reachable' pieces on the board for some player
        valid = {}
        piece_map = self.piece_map
            
        for (x,y,z), value in piece_map.items():
            if value == player:
                for offset in DIRECTIONS.values():
                    delta = 1
                    while True:
                        x2 = x + offset[0]*delta
                        y2 = y + offset[1]*delta
                        z2 = z + offset[2]*delta
                        tile = piece_map.get((x2, y2, z2))
                        if tile is None:
                            x2 = x + offset[0]*(delta)
                            y2 = y + offset[1]*(delta)
                            z2 = z + offset[2]*(delta)
                            if 2 <= self.neighbour_count((x2, y2, z2), ignore_piece=origin) < 5:
                                valid[(x2, y2, z2)] = valid.get((x2, y2, z2), 0) + 1
                            break
                        if tile == 'N':
                            delta += 1
                        else:
                            break
        return dict(sorted(valid.items(), key=lambda item: item[1], reverse=True)[:3])

    def get_candidate_destinations(self):
        candidates = set()
        piece_map = self.piece_map

        for (x,y,z) in piece_map:
            for dx, dy, dz in DIRECTIONS.values():
                neighbour = (x+dx, y+dy, z+dz)

                if neighbour not in piece_map:
                    candidates.add(neighbour)

        return candidates
    
    def get_disc_destinations(self, origin, filtered=False, player=None):
        if filtered and player in ('R', 'B'):
            return self.convergent_destinations(player, origin)
        valid = []
        piece_map = self.piece_map
        directions = DIRECTIONS.values()

        candidates = self.get_candidate_destinations()

        for (x,y,z) in candidates:
            count = 0

            for dx, dy, dz in directions:
                neighbour = (x+dx, y+dy, z+dz)

                if neighbour == origin:
                    continue

                if neighbour in piece_map:
                    count += 1
                    if count > 4:
                        break
            
            if 2 <= count <= 4:
                valid.append((x, y, z))
        
        return valid
    
    def get_disc_moves(self):
        all_moves = []

        movable = self.get_disc_origins()
        for origin in movable:
            destinations = self.get_disc_destinations(origin)
            for destination in destinations:
                all_moves.append(((origin), (destination)))
        
        return all_moves
    
    def get_all_moves(self, player):
        all_moves = []

        tokens = self.get_token_moves(player)
        for token in tokens:
            copy_board = Board(piece_map=copy.deepcopy(self.piece_map))
            copy_board.move_token(token[0], token[1], player)
            disc_move = copy_board.get_disc_moves()
            for move in disc_move:
                all_moves.append((token, move))

        return all_moves
    
    def get_all_filtered_moves(self, player):
        all_moves = []

        tokens = self.get_token_moves(player)
        for token in tokens:
            copy_board = Board(piece_map=copy.deepcopy(self.piece_map))
            copy_board.move_token(token[0], token[1], player)
            # Get the filtered disc moves.
            origins = copy_board.get_disc_origins(filtered=True, player=player)
            for origin in origins:
                destinations = copy_board.get_disc_destinations(origin, filtered=True, player=player)
                for destination in destinations:
                    all_moves.append((token, (origin, destination)))
        
        return all_moves
    
    def apply_move(self, board, move, player):
        (token_move, disc_move) = move
        (coord, direction) = token_move
        (origin, destination) = disc_move

        assert(board.move_token(coord, direction, player))
        assert(board.move_disc(origin, destination))
        
        return True
    
if __name__ == "__main__":
    board = Board()
    board.create_board()
    moves = board.get_all_filtered_moves('R')
    print(len(moves))