# Game Logic

import time
import cProfile

class BoardPiece:
    def __init__(self, coords, occupation, just_moved):
        self.coords = coords
        self.occupation = occupation
        self.just_moved = just_moved

    def get_coords(self):
        return self.coords

    def get_occupation(self):
        return self.occupation

    def get_just_moved(self):
        return self.just_moved

    def set_coords(self, new_coords):
        self.coords = new_coords

    def set_occupation(self, new_occupation):
        self.occupation = new_occupation

    def set_just_moved(self):
        self.just_moved = not self.just_moved

    def print(self):
        print(f"{self.coords}, {self.occupation}")

class Board:
    def __init__(self):
        self.pieces = []
        self.coord_map = {}

    def create_board(self):
        self.pieces = []
        self.coord_map = {}

        piece_coords = [
            (x, y, z)
            for x in [-2, -1, 0, 1, 2]
            for y in [-2, -1, 0, 1, 2]
            for z in [-2, -1, 0, 1, 2]
            if x + y + z == 0
        ]

        for coord in piece_coords:
            if coord == (-2, 1, 1) or coord == (1, -2, 1) or coord == (1, 1, -2):
                p = BoardPiece(coord, 'r', False)
            elif coord == (-1, 2, -1) or coord == (2, -1, -1) or coord == (-1, -1, 2):
                p = BoardPiece(coord, 'b', False)
            else:
                p = BoardPiece(coord, 'N', False)
            self.pieces.append(p)
            self.coord_map[coord] = p


    def get_pieces(self):
        return self.pieces


    def move_player(self, location, direction):

        player_piece = self.coord_map.get(location)

        if player_piece == None:
            return "No piece at that location"

        occupation = player_piece.get_occupation()

        if occupation == 'N':
            return "Not an occupied piece"

        directions = {
            "ur": (1, 0, -1),
            "mr": (1, -1, 0),
            "dr": (0, -1, 1),
            "dl": (-1, 0, 1),
            "ml": (-1, 1, 0),
            "ul": (0, 1, -1)
        }

        if direction not in directions:
            return "Not a valid direction"

        dx, dy, dz = directions[direction]

        current_coords = location
        new_coords = location

        while True:
            next_coords = (
                current_coords[0] + dx,
                current_coords[1] + dy,
                current_coords[2] + dz
            )

            if not self.check_location(next_coords):
                break

            new_coords = next_coords
            current_coords = next_coords

        if new_coords == location:
            return

        player_piece.set_occupation('N')

        self.coord_map[new_coords].set_occupation(occupation)

        return new_coords



    def check_piece(self, location, new=False):
        # When it comes to moving a piece, we want to ensure that we do not need to move any other pieces, so enforce < 5 neighbours
        # For its new location, it must touch at least 2 other pieces

        neighbour_offset = [(1, -1, 0),
                            (1, 0, -1),
                            (0, 1, -1),
                            (0, -1, 1),
                            (-1, 0, 1),
                            (-1, 1, 0)
                            ]

        x,y,z = location

        piece_border_count = sum(
            1 for dx,dy,dz in neighbour_offset
            if self.coord_map.get((x+dx, y+dy, z+dz)) is not None
        )

        if new:
            return piece_border_count > 1
        return piece_border_count < 5



    def move_piece(self, old_location, new_location):
        if self.check_piece(old_location):
            if self.check_piece(new_location, new=True):
                piece = self.coord_map.get(old_location)
                if piece is None:
                    return "No piece there"
                if piece.get_occupation() != 'N':
                    return "Unoccupied position"
                if piece.get_just_moved():
                    return "Cannot move a piece just moved"
                
                del self.coord_map[old_location]
                piece.set_coords(new_location)
                self.coord_map[new_location] = piece

                for old_piece in self.pieces:
                    if old_piece.get_just_moved():
                        old_piece.set_just_moved()
                piece.set_just_moved()
                return True
        return False



    def check_location(self, location):
        piece = self.coord_map.get(location)
        return piece is not None and piece.occupation == "N"

    def check_win(self, occupation):
        # 3 possible shapes to result in a win, a line, a triangle, and a tick

        neighbour_offset = [(1, -1, 0),
                            (1, 0, -1),
                            (0, 1, -1),
                            (0, -1, 1),
                            (-1, 0, 1),
                            (-1, 1, 0)
                            ]

        for piece in self.pieces:
            if piece.occupation != occupation:
                continue

            neighbour_count = 0
            x, y, z = piece.get_coords()

            for dx, dy, dz in neighbour_offset:
                neighbour = (x+dx, y+dy, z+dz)
                p = self.coord_map.get(neighbour)
                if p is not None and p.occupation == occupation:
                    neighbour_count += 1

            if neighbour_count == 2:
                return f"win {occupation}"

        return None

    def string_to_tuple(self, string):
        parts = string.split(',')
        return tuple(int(part) for part in parts)

    def parse_move(self, input):
        # "example move 'mp 0,2,-2 ul mb 2,0,-2 4,2,-2;'"

        input = input.strip()
        commands = input.split()

        commands[-1] = commands[-1][:-1]

        i = 0

        while i < len(commands):
            if commands[i] == "mp":
                self.move_player(self.string_to_tuple(commands[i + 1]), commands[i + 2])
                i += 3
            elif commands[i] == "mb":
                self.move_piece(self.string_to_tuple(commands[i + 1]), self.string_to_tuple(commands[i + 2]))
                i += 3
            else:
                i += 1

    # FUNCTIONS BELOW FOR MINIMAX ALGORITHM

    def get_valid_player_moves(self, occupation):
        directions = ['ur', 'mr', 'dr', 'dl', 'ml', 'ul']
        moves = []

        for piece in self.pieces:
            if piece.get_occupation() == occupation:
                for direction in directions:
                    moves.append((piece.get_coords(), direction))
        
        return moves
    
    def get_valid_piece_destinations(self, removed_piece):
        directions = [
            (1, 0, -1), (1, -1, 0), (0, 1, -1),
            (0, -1, 1), (-1, 0, 1), (-1, 1, 0)
        ]

        possible_moves = set()

        candidates = set()

        for piece in self.pieces:
            if piece.get_coords() == removed_piece:
                continue

            x, y, z = piece.get_coords()

            for dx, dy, dz in directions:
                neighbour = (x + dx, y + dy, z + dz)

                if self.coord_map.get(neighbour) is None:
                    candidates.add(neighbour)
        
        for candidate in candidates:
            cx, cy, cz = candidate
            neighbour_count = 0
            for dx, dy, dz in directions:
                check = (cx + dx, cy + dy, cz + dz)
                if check != removed_piece and self.coord_map.get(check) is not None:
                    neighbour_count += 1
                    if neighbour_count >= 2:
                        break

            if 2 <= neighbour_count:
                possible_moves.add(candidate)

        return list(possible_moves)

    def get_valid_piece_moves(self):
        moves = []

        for piece in self.pieces:
            if piece.get_occupation() != 'N' or not self.check_piece(piece.get_coords()) or piece.get_just_moved():
                continue

            destinations = self.get_valid_piece_destinations(piece.get_coords())
            for dest in destinations:
                moves.append((piece.get_coords(), dest))
        
        return moves

    def get_all_moves(self, occupation):
        player_moves = self.get_valid_player_moves(occupation)
        all_moves = []
        directions = [(1,0,-1),(1,-1,0),(0,1,-1),(0,-1,1),(-1,0,1),(-1,1,0)]

        piece_destination_cache = {}
        for piece in self.pieces:
            if piece.get_occupation() == 'N' and self.check_piece(piece.get_coords()) and not piece.get_just_moved():
                coord = piece.get_coords()
                piece_destination_cache[coord] = self.get_valid_piece_destinations(coord)
        
        for pm in player_moves:
            new_player_coords = self.move_player(pm[0], pm[1])
            if new_player_coords is None:
                continue

            affected = set()
            for dx, dy, dz in directions:
                affected.add((pm[0][0]+dx, pm[0][1]+dy, pm[0][2]+dz))
                if new_player_coords:
                    affected.add((new_player_coords[0] + dx, new_player_coords[1] + dy, new_player_coords[2] + dz))
            
            for coord, dests in piece_destination_cache.items():
                if coord == new_player_coords:
                    continue

                if coord in affected:
                    recomputed = self.get_valid_piece_destinations(coord)
                    for dest in recomputed:
                        all_moves.append((pm, (coord, dest)))
                else:
                    for dest in dests:
                        all_moves.append((pm, (coord, dest)))

            self.coord_map[new_player_coords].set_occupation('N')
            self.coord_map[pm[0]].set_occupation(occupation)

        all_moves.sort(
            key=lambda m: self.score_move_for_ordering(m, occupation),
            reverse = True
        )
        
        return all_moves


    def apply_move(self, move):
        pm, bm = move

        original_player_coords = pm[0]
        new_player_coords = self.move_player(pm[0], pm[1])

        prev_just_moved = next((p.get_coords() for p in self.pieces if p.get_just_moved()), None)

        result = self.move_piece(bm[0], bm[1])
        assert result == True

        return (pm, bm, original_player_coords, new_player_coords, prev_just_moved)


    def undo_move(self, move_record):
        pm, bm, original_player_coords, new_player_coords, prev_just_moved = move_record

        for piece in self.pieces:
            piece.just_moved = False

        if prev_just_moved:
            p = self.coord_map.get(prev_just_moved)
            if p:
                p.set_just_moved()

        piece = self.coord_map.get(bm[1])
        if piece:
            del self.coord_map[bm[1]]
            piece.set_coords(bm[0])
            self.coord_map[bm[0]] = piece

        piece = self.coord_map.get(new_player_coords)
        if piece:
            occupation = piece.get_occupation()
            piece.set_occupation('N')
            original = self.coord_map.get(original_player_coords)
            if original:
                original.set_occupation(occupation)


    def evaluate_board(self, occupation):
        opponent = 'b' if occupation == 'r' else 'r'
        directions = [(1, -1, 0), (1, 0, -1), (0, 1, -1), (0, -1, 1), (-1, 0, 1), (-1, 1, 0)]

        score = 0
        for piece in self.pieces:
            if piece.get_occupation() not in (occupation, opponent):
                continue

            x, y, z = piece.get_coords()
            occ = piece.get_occupation()

            neighbours = sum(
                1 for dx, dy, dz in directions
                if self.coord_map.get((x+dx, y+dy, z+dz)) is not None
                and self.coord_map[(x+dx, y+dy, z+dz)].occupation == occ
            )

            if piece.get_occupation() == occupation:
                score += neighbours ** 2
            else:
                score -= neighbours ** 2

        return score
    
    def score_move_for_ordering(self, move, occupation):
        pm, bm = move
        directions = [(1,0,-1),(1,-1,0),(0,1,-1),(0,-1,1),(-1,0,1),(-1,1,0)]
        coord_map = self.coord_map

        px, py, pz = pm[0]
        friendly_neighbours = 0

        for dx, dy, dz in directions:
            if coord_map.get((px+dx, py+dy, pz+dz)) is not None and coord_map[(px+dx, py+dy, pz+dz)].occupation == occupation:
                friendly_neighbours += 1

        return friendly_neighbours

        
    
    def minimax(self, depth, maximising, occupation, alpha = float('-inf'), beta = float('inf')):
        opponent = 'b' if occupation == 'r' else 'r'

        if depth == 0:
            return self.evaluate_board(occupation), None
    
        best_move = None

        if maximising:
            best_score = float('-inf')
            for move in self.get_all_moves(occupation):
                record = self.apply_move(move)
                score, _ = self.minimax(depth - 1, False, occupation, alpha, beta)
                self.undo_move(record)

                if score > best_score:
                    best_score = score
                    best_move = move

                alpha = max(alpha, best_score)

                if beta <= alpha:
                    break

            return best_score, best_move
        
        else:
            best_score = float('inf')
            for move in self.get_all_moves(opponent):
                record = self.apply_move(move)
                score, _ = self.minimax(depth - 1, True, occupation, alpha, beta)
                self.undo_move(record)

                if score < best_score:
                    best_score = score
                    best_move = move

                beta = min(beta, best_score)

                if beta <= alpha:
                    break

            return best_score, best_move

board = Board()
board.create_board()

start = time.time()

score, move = board.minimax(2, True, 'r')

print(f"Time taken: {time.time() - start:.2f}s")

print(f"Best score: {score}")
print(f"Bestmove: {move}")
#cProfile.run("board.minimax(2, True, 'r')")