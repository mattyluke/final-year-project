# Board is made up of pieces with x, y, z coordinates
# BoardPiece has x,y,z coordinates and an occupation

# Red player moves red occupations, Black player moves black occupations

# After every move, check win condition

# If not won, allow them to move a piece, it must be touching at max 3 pieces, and in its new position it must touch at least 2

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



    def create_board(self):
        self.pieces = []

        piece_coords = [
            (x, y, z)
            for x in [-2, -1, 0, 1, 2]
            for y in [-2, -1, 0, 1, 2]
            for z in [-2, -1, 0, 1, 2]
            if x + y + z == 0
        ]

        for coord in piece_coords:
            if coord == (-2, 1, 1) or coord == (1, -2, 1) or coord == (1, 1, -2):
                self.pieces.append(BoardPiece(coord, 'r', False))
            elif coord == (-1, 2, -1) or coord == (2, -1, -1) or coord == (-1, -1, 2):
                self.pieces.append(BoardPiece(coord, 'b', False))
            else:
                self.pieces.append(BoardPiece(coord, 'N', False))


    def get_pieces(self):
        return self.pieces


    def move_player(self, location, direction):

        player_piece = None
        for piece in self.pieces:
            if piece.coords == location:
                player_piece = piece
                break

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

        for piece in self.pieces:
            if piece.coords == new_coords:
                piece.set_occupation(occupation)
                break

        return self.check_win(occupation)



    def check_piece(self, location, new=False):
        # When it comes to moving a piece, we want to ensure that we do not need to move any other pieces, so enforce < 5 neighbours
        # For its new location, it must touch at least 2 other pieces

        piece_border_count = 0

        neighbour_offset = {(1, -1, 0),
                            (1, 0, -1),
                            (0, 1, -1),
                            (0, -1, 1),
                            (-1, 0, 1),
                            (-1, 1, 0)
                            }

        for piece in self.pieces:
            coords = piece.get_coords()
            delta = (
                coords[0] - location[0],
                coords[1] - location[1],
                coords[2] - location[2]
            )

            if delta in neighbour_offset:
                piece_border_count += 1

        if new:
            return piece_border_count > 1
        return piece_border_count < 5



    def move_piece(self, old_location, new_location):
        if self.check_piece(old_location):
            if self.check_piece(new_location, new=True):
                for piece in self.pieces:
                    if piece.coords == old_location:
                        if piece.get_occupation() != 'N':
                            return "Unoccupied position"
                        if piece.get_just_moved() == True:
                            return "Cannot move a piece just moved"
                        piece.set_coords(new_location)
                        for old_piece in self.pieces:
                            if old_piece.get_just_moved() == True:
                                old_piece.set_just_moved()
                        piece.set_just_moved()
                        return True
        return False



    def check_location(self, location):
        for piece in self.pieces:
            if piece.coords == location and piece.occupation == 'N':
                return True
        return False

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
                neighbour = (x + dx, y + dy, z + dz)

                for other in self.pieces:
                    if other.coords == neighbour and other.occupation == occupation:
                        neighbour_count += 1
                        break

            if neighbour_count == 2:
                return f"win {occupation}"

        return None



    def print_board(self):
        for piece in self.pieces:
            piece.print()


    def string_to_tuple(self, string):
        numbers = []
        num = ""

        for char in string:
            if char.isdigit():
                num += char
                continue
            if char == "n":
                numbers.append(-int(num))
                num = ""
            if char == "p":
                numbers.append(int(num))
                num = ""

        result = tuple(numbers)
        return result

    def parse_move(self, input):
        # "example move 'mp 0p2p2n ul mb 2p0p2n 4p2p2n'"

        input = input.strip()
        commands = input.split()

        if commands[0] == "mp":
            state = self.move_player(self.string_to_tuple(commands[1]), commands[2])
            return state
        if commands[0] == "mb":
            self.move_piece(self.string_to_tuple(commands[1]), self.string_to_tuple(commands[2]))
        if commands[0] == "print":
            self.print_board()