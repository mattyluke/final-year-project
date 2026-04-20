# Game Logic

# Directions: {'ur': (1, 0, -1), 'mr': (1, -1, 0), 'dr': (0, -1, 1), 'dl': (-1, 0, 1), 'ml': (-1, 1, 0), 'ul': (0, 1, -1)}

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

class Board:
    def __init__(self):
        self.coords = [(-2, 0), (-2, 1), (-2, 2), (-1, -1), (-1, 0), 
                       (-1, 1), (-1, 2), (0, -2), (0, -1), (0, 0), 
                       (0, 1), (0, 2), (1, -2), (1, -1), (1, 0), 
                       (1, 1), (2, -2), (2, -1), (2, 0)]
        self.movable_discs = {11, 15, 18, 17, 16, 12, 7, 3, 0, 1, 2, 6}
        self.candidates = {(-2, -1), (-1, -2), (1, -3), (2, -3), (3, -2), (3, -1), (2, 1), (1, 2), (-1, 3), (-2, 3), (-3, 2), (-3, 1)}
        self.index = {coord: i for i, coord in enumerate(self.coords)}
        self.neighbour_count = [3, 4, 3, 4, 6, 6, 4, 3, 6, 6, 6, 3, 4, 6, 6, 4, 3, 4, 3]
        self.board = [0] * 19
        self.board[1] = BLACK
        self.board[3] = RED
        self.board[6] = RED
        self.board[12] = BLACK
        self.board[15] = BLACK
        self.board[17] = RED

        self.red_i = {3, 6, 17}
        self.black_i = {1, 12, 15}
        self.last_moved_disc = None
    
    def move_token(self, i, DIR):
        plyr = self.board[i]
        x, y = self.coords[i]
        dx, dy = DIRECTIONS[DIR]

        last_valid_i = i

        while True:
            x += dx
            y += dy

            next_i = self.index.get((x, y))

            if next_i is None:
                break

            if self.board[next_i] != EMPTY:
                break

            last_valid_i = next_i
        
        if last_valid_i == i:
            return False
        
        self.board[i] = EMPTY
        self.board[last_valid_i] = plyr

        if plyr == 1:
            self.red_i.discard(i)
            self.red_i.add(last_valid_i)
        
        elif plyr == 2:
            self.black_i.discard(i)
            self.black_i.add(last_valid_i)

        new_movable = None
        if 2 <= self.neighbour_count[i] <= 4 and self.board[i] == EMPTY:
            self.movable_discs.add(i)
            new_movable = i
        was_movable = last_valid_i in self.movable_discs
        self.movable_discs.discard(last_valid_i)

        return i, last_valid_i, new_movable, was_movable
    
    # i - index of moved piece, coord - coord of new piece
    def move_disc(self, i, coord):
        old_coord = self.coords[i]
        self.index[coord] = self.index.pop(old_coord)
        self.coords[i] = coord
        # Lower all old neighbours neighbour count by 1, increase all new ones by 1 and recompute moved discs neighbour
        old_x, old_y = old_coord
        new_x, new_y = coord
        old_neighbours = []
        new_neighbours = []

        for dx, dy in DIRECTIONS:
            old_neighbour = (old_x + dx, old_y + dy)
            new_neighbour = (new_x + dx, new_y + dy)
            if old_neighbour in self.index:
                old_neighbours.append(self.index[old_neighbour])
            if new_neighbour in self.index:
                new_neighbours.append(self.index[new_neighbour])
        
        for idx in old_neighbours:
            self.neighbour_count[idx] -= 1
        for idx in new_neighbours:
            self.neighbour_count[idx] += 1
        self.neighbour_count[i] = len(new_neighbours)
    
        recheck = [i] + old_neighbours + new_neighbours

        for idx in recheck:
            if 2 <= self.neighbour_count[idx] <= 4 and self.board[idx] == EMPTY:
                if idx not in self.movable_discs:
                    self.movable_discs.add(idx)
            else:
                if idx in self.movable_discs:
                    self.movable_discs.discard(idx)

        for dx, dy in DIRECTIONS:
            old_count = 0
            for ox, oy in [old_coord, coord]:
                neighbour = (ox + dx, oy + dy)
                if neighbour not in self.index:
                    count = sum(1 for ddx, ddy in DIRECTIONS
                                if (neighbour[0] + ddx, neighbour[1] + ddy) in self.index)
                    if 2 <= count <= 4:
                        if neighbour not in self.candidates:
                            self.candidates.add(neighbour)
                    else:
                        if neighbour in self.candidates:
                            self.candidates.discard(neighbour)
                else:
                    old_count += 1
        count = sum(1 for dx, dy in DIRECTIONS
                    if (old_coord[0] + dx, old_coord[1] + dy) in self.index)
        if 2 <= count <= 4:
            if old_coord not in self.candidates:
                self.candidates.add(old_coord)
        else:
            if old_coord in self.candidates:
                self.candidates.discard(old_coord)

        self.candidates.discard(coord)

        prev_moved_disc = self.last_moved_disc
        self.last_moved_disc = i

        return i, old_coord, prev_moved_disc
    
    def check_win(self, player):
        pieces = self.red_i if player == RED else self.black_i
        a, b, c = pieces
        ax, ay = self.coords[a]
        bx, by = self.coords[b]
        cx, cy = self.coords[c]

        ab = (bx-ax, by-ay) in DIRECTIONS
        bc = (cx-bx, cy-by) in DIRECTIONS
        ac = (cx-ax, cy-ay) in DIRECTIONS

        return (ab and bc) or (ab and ac) or (bc and ac)
    
    def generate_token_moves(self, player):
        pieces = self.red_i if player == RED else self.black_i
        moves = []
        for i in pieces:
            x, y = self.coords[i]
            for DIR in range(6):
                dx, dy = DIRECTIONS[DIR]
                nx, ny = x + dx, y + dy
                next_i = self.index.get((nx, ny))
                if next_i is not None and self.board[next_i] == EMPTY:
                    moves.append(('token', i, DIR))
        return moves
    
    def generate_disc_moves(self):
        moves = []
        for i in self.movable_discs:
            if i == self.last_moved_disc:
                continue
            for coord in self.candidates:
                moves.append(('disc', i, coord))
        return moves
    
    # board[new_i] -> board[old_i]
    def undo_token_move(self, old_i, new_i, new_movable, was_movable):
        plyr = self.board[new_i]
        self.board[old_i] = plyr
        self.board[new_i] = EMPTY
        if plyr == RED:
            self.red_i.discard(new_i)
            self.red_i.add(old_i)
        else:
            self.black_i.discard(new_i)
            self.black_i.add(old_i)
        if new_movable:
            self.movable_discs.add(new_movable)
        if was_movable:
            self.movable_discs.add(new_i)
    
    def undo_disc_move(self, i, old_coord, prev_moved_disc):
        # change new_coord to the old coord
        self.move_disc(i, old_coord)
        self.last_moved_disc = prev_moved_disc
    
    # generate all moves, simulate all token moves and then add all possible moved pieces with candidates
    def generate_all_moves(self, player):
        moves = []
        token_moves = self.generate_token_moves(player)
        for token_move in token_moves:
            old_i, new_i, new_movable, was_movable = self.move_token(token_move[1], token_move[2])
            disc_moves = self.generate_disc_moves()
            for disc_move in disc_moves:
                moves.append((token_move, disc_move))
            self.undo_token_move(old_i, new_i, new_movable, was_movable)

        return moves