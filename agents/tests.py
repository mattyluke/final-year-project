from game_engine import Board
from evaluation import cluster_score
import unittest

# We want piece_map to be equal to all pieces w/ coords (x, y, z) s.t. if two of the numbers are 1 then its value is 'R', if two of the numbers are -1 then its value is
# B, and then N otherwise. The only constraints are -2 <= x, y, z <= 2 and x + y + z = 0.

class TestInitialMap(unittest.TestCase):

    def test_piece_map_rules(self):
        board = Board()
        board.create_board()
        piece_map = board.get_board()

        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue

                    self.assertIn((x,y,z), piece_map)

                    value = piece_map[(x, y, z)]
                    coords = [x, y, z]

                    if coords.count(1) == 2:
                        self.assertEqual(value, 'R')
                    elif coords.count(-1) == 2:
                        self.assertEqual(value, 'B')
                    else:
                        self.assertEqual(value, 'N')

class TestOccupationGuard(unittest.TestCase):
    def test_occupation_enforcement(self):
        board = Board()
        board.create_board()
        self.assertFalse(board.move_token((-2, 1, 1), 'ur', 'B'))

class TestInvalidDirectionMovement(unittest.TestCase):
    def test_occupation_enforcement(self):
        board = Board()
        board.create_board()
        self.assertFalse(board.move_token((-2, 1, 1), 'dl', 'R'))

class TestPlayerMovementBoundaries(unittest.TestCase):
    def test_player_moves_bounds(self):
        test_board = {}

        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    test_board[(x, y, z)] = 'N'
                    if x == 0 and y == 0 and z == 0:
                        test_board[(x, y, z)] = 'R'
        
        # We want to enforce boundaries, is the player able to move to a location off the board? Also if a player moves, is their last location empty?
        # This creates an empty Hex grid with radius 2, we will place the player in the center (0, 0, 0) and try all 6 directions and compare against expected values.

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'ur', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(2, 0, -2)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'mr', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(2, -2, 0)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'dr', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(0, -2, 2)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'dl', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(-2, 0, 2)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'ml', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(-2, 2, 0)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'ul', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(0, 2, -2)], 'R')

class TestPlayerMovementBlocked(unittest.TestCase):
    def test_player_moves_blocking(self):
        test_board = {}

        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    test_board[(x, y, z)] = 'N'
                    if x == 0 and y == 0 and z == 0:
                        test_board[(x, y, z)] = 'R'
                    # This check puts pieces on every edge of the Hexagon board, then we make sure that the player is being blocked by them.
                    if [x, y, z].count(2) == 1 and [x, y, z].count(0) == 1:
                        test_board[(x, y, z)] = 'B'

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'ur', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(1, 0, -1)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'mr', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(1, -1, 0)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'dr', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(0, -1, 1)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'dl', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(-1, 0, 1)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'ml', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(-1, 1, 0)], 'R')

        board = Board(piece_map = test_board.copy())
        self.assertTrue(board.move_token((0, 0, 0), 'ul', 'R'))
        self.assertEqual(board.get_board()[(0, 0, 0)], 'N')
        self.assertEqual(board.get_board()[(0, 1, -1)], 'R')

class TestCyclicMovement(unittest.TestCase):
    # Now testing chaining moves, this one makes sure that after multiple moves on a board, we end up where we expect, in this instance we are going to move around the
    # edge of the board, start pos -> mr -> ur -> ul -> ml -> dl -> dr, tests all 6 movements.
    def test_player_moves_cycle(self):
        test_board = {}

        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    test_board[(x, y, z)] = 'N'
                    if x == -2 and y == 0 and z == 2:
                        test_board[(x, y, z)] = 'R'
        
        board = Board(piece_map=test_board)
        self.assertTrue(board.move_token((-2, 0, 2), 'mr', 'R'))
        self.assertTrue(board.move_token((0, -2, 2), 'ur', 'R'))
        self.assertTrue(board.move_token((2, -2, 0), 'ul', 'R'))
        self.assertTrue(board.move_token((2, 0, -2), 'ml', 'R'))
        self.assertTrue(board.move_token((0, 2, -2), 'dl', 'R'))
        self.assertTrue(board.move_token((-2, 2, 0), 'dr', 'R'))

        self.assertEqual(board.get_board()[(-2, 0, 2)], 'R')


class TestBlockedMovement(unittest.TestCase):
    # Now testing some blocked movement, if we hit a player, and then decide to move, does our new movement location accurately reflect the blocked movement?
    def test_player_moves_cycle(self):
        test_board = {}

        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    test_board[(x, y, z)] = 'N'
                    if x == 0 and y == 0 and z == 0:
                        test_board[(x, y, z)] = 'R'
                    if x == 2 and y == -2 and z == 0:
                        test_board[(x, y, z)] = 'B'
        
        board = Board(piece_map=test_board)
        self.assertTrue(board.move_token((0, 0, 0), 'mr', 'R'))
        self.assertTrue(board.move_token((1, -1, 0), 'dl', 'R'))
        self.assertEqual(board.get_board()[(-1, -1, 2)], 'R')

class TestPieceMovement(unittest.TestCase):
    def test_piece_movement(self):
        # Want to verify a few things here:
        # 1. If a piece is occupied, we cannot move it
        # 2. If a piece has too many neighbours, we cannot move it
        # 3. If a piece destination has too little neighbours, then we cannot move it
        # 4. If a piece destination has too many neighbours, then we cannot move it
        # 5. If original location does not exist, no piece to move
        # 6. If new location already exists, we can't move there

        # To test for 3. I am going to move -2, 0, 2 from its original position to 3, 0, -3.
        # To test for 4. I am going to add pieces (2, -3, 1), (2, -4, 2), (1, -4, 3), this should make possible location (1, -3, 2) have too many neighbours.
        test_board = {}

        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    if x == -2 and y == 0 and z == 2:
                        test_board[(3, 0, -3)] = 'N'
                    elif x == -2 and y == 2 and z == 0:
                        test_board[(x, y, z)] = 'R'
                    else:
                        test_board[(x, y, z)] = 'N'
        
        test_board[(2, -3, 1)] = 'N'
        test_board[(2, -4, 2)] = 'N'
        test_board[(1, -4, 3)] = 'N'
        
        board = Board(piece_map=test_board)

        self.assertFalse(board.move_disc((-2, 2, 0), (-1, 3, 2)))
        self.assertFalse(board.move_disc((0, 0, 0), (-1, 3, 2)))
        self.assertFalse(board.move_disc((2, -2, 0), (4, -1, -3)))
        self.assertFalse(board.move_disc((2, -2, 0), (1, -3, 2)))
        self.assertFalse(board.move_disc((-4, 0, 4), (1, -3, 2)))
        self.assertFalse(board.move_disc((2, -2, 0), (0, 2, -2)))

        # Now for legal movements, can we move 2, -2, 0 to -1, 3, -2?

        self.assertTrue(board.move_disc((2, -2, 0), (-1, 3, -2)))

class TestJustMoved(unittest.TestCase):
    def test_just_moved_piece(self):
        board = Board()
        board.create_board()
        self.assertTrue(board.move_disc((-2, 2, 0), (3, -2, -1)))
        self.assertEqual(board.get_just_moved(), (3, -2, -1))


class TestWinCondition(unittest.TestCase):
    # Three possible shapes are made when a game of Nonaga is won, a triangle, a line, and a hook, we should check all 3 cases correctly result in a victory.

    def test_wins(self):
        # Test a triangle, (1, 0, -1) and (1, -1, 0) are occupied by red, so red moves from (-2, 0, 2) ur to (0, 0, 0) connecting all 3 pieces, this should return True
        test_board = {}
        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    if (x == 1 and y == 0 and z == -1) or (x == 1 and y == -1 and z == 0):
                        test_board[(x, y, z)] = 'R'
                    else:
                        test_board[(x, y, z)] = 'N'

        test_board[(-2, 0, 2)] = 'R'

        board = Board(piece_map=test_board)

        self.assertTrue(board.move_token((-2, 0, 2), 'ur', 'R'))
        self.assertTrue(board.check_win())

        # Test a hook, (1, 0, -1) and (1, -1, 0) are occupied by red, so red moves from (-1, 2, -1) mr to (0, 1, -1), connecting all 3 pieces
        test_board = {}
        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    if (x == 1 and y == 0 and z == -1) or (x == 1 and y == -1 and z == 0):
                        test_board[(x, y, z)] = 'R'
                    else:
                        test_board[(x, y, z)] = 'N'
        
        test_board[(-1, 2, -1)] = 'R'

        board = Board(piece_map=test_board)

        self.assertTrue(board.move_token((-1, 2, -1), 'mr', 'R'))
        self.assertTrue(board.check_win())

        # Test a line, (1, 0, -1) and (1, -1, 0) are occupied by red, so red moves from (-2, 1, 1) ur to (1, 1, -2) connecting all 3 pieces, this should return True
        test_board = {}
        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    if (x == 1 and y == 0 and z == -1) or (x == 1 and y == -1 and z == 0):
                        test_board[(x, y, z)] = 'R'
                    else:
                        test_board[(x, y, z)] = 'N'

        test_board[(-2, 1, 1)] = 'R'

        board = Board(piece_map=test_board)

        self.assertTrue(board.move_token((-2, 1, 1), 'ur', 'R'))
        self.assertTrue(board.check_win())

class TestPossibleTokenMoves(unittest.TestCase):
    def test_tokens(self):
        board = Board()
        board.create_board()
        possible = board.get_token_moves('R')
        self.assertCountEqual(possible, [((-2, 1, 1), 'dr'), ((-2, 1, 1), 'mr'), ((-2, 1, 1), 'ur'), ((-2, 1, 1), 'ul'), ((1, -2, 1), 'dl'), ((1, -2, 1), 'ml'), ((1, -2, 1), 'ul'), ((1, -2, 1), 'ur'), ((1, 1, -2), 'ml'), ((1, 1, -2), 'dl'), ((1, 1, -2), 'dr'), ((1, 1, -2), 'mr')])

class TestPossibleBoardDestinations(unittest.TestCase):
    def test_dest(self):
        board = Board()
        board.create_board()
        possible = board.get_disc_destinations((-2, 0, 2))
        self.assertCountEqual(possible, [(-1, -2, 3), (1, -3, 2), (2, -3, 1), (3, -2, -1), (3, -1, -2), (2, 1, -3), (1, 2, -3), (-1, 3, -2), (-2, 3, -1), (-3, 2, 1)])

class TestClusterScore(unittest.TestCase):

    # Check that our pieces being closer together evaluates some state better than the opponents 

    def test_dest(self):
        test_board = {}
        for x in range(-2, 3):
            for y in range(-2, 3):
                for z in range(-2, 3):
                    if x + y + z != 0:
                        continue
                    if (x == 0 and y == 0 and z == 0) or (x == 1 and y == 0 and z == -1) or (x == 1 and y == -1 and z == 0):
                        test_board[(x, y, z)] = 'R'
                    elif (x == -1 and y == 2 and z == -1) or (x == 2 and y == -1 and z == -1) or (x == -1 and y == -1 and z == 2):
                        test_board[(x, y, z)] = 'B'
                    else:
                        test_board[(x, y, z)] = 'N'

        board = Board(piece_map=test_board)

        self.assertGreater(cluster_score(board, 'R'), cluster_score(board, 'B'))
        

if __name__ == "__main__":
    unittest.main()