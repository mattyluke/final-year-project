from mcts import run_worker
from game_engine import Board
from multiprocessing import Pool
import socket, json

# Receive a board state, i.e. list of coords, index is not important since the pairings are arbitrary, and we can use that board state to compute the movable and candidate discs, performance is
# not as important compared to the arena so we can stand the computation time
# Will also need red coords and black coords, as well as last moved disc

# Upon generating a move, send it to the server, which will then turn it into a state which the renderer can display

# Receiving socket -> [coords, last_moved, red_coords, black_coords, colour, gameId], gameId so the server knows which game to send the new state to.

STR_DIRECTIONS = ['ur', 'mr', 'dr', 'dl', 'ml', 'ul']
DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
EMPTY = 0
RED = 1
BLACK = 2
_pool = None

def create_board(data):
    board = Board()
    board.board = [EMPTY] * 19
    board.red_i = set()
    board.black_i = set()
    incoming_coords = [tuple(c) for c in data['coords']]
    board.coords = incoming_coords
    board.index = {coord: i for i, coord in enumerate(incoming_coords)}

    for coord in data['red_coords']:
        i = board.index[tuple(coord)]
        board.board[i] = RED
        board.red_i.add(i)
    
    for coord in data['black_coords']:
        i = board.index[tuple(coord)]
        board.board[i] = BLACK
        board.black_i.add(i)
    
    if data['last_moved']:
        board.last_moved_disc = board.index[tuple(data['last_moved'])]
    else:
        board.last_moved_disc = None

    board.movable_discs = set()
    for i, coord in enumerate(board.coords):
        if board.board[i] == EMPTY:
            count = sum(1 for dq, dr in DIRECTIONS if (coord[0] + dq, coord[1] + dr) in board.index)
            if 2 <= count <= 4:
                board.movable_discs.add(i)
    if board.last_moved_disc is not None:
        board.movable_discs.discard(board.last_moved_disc)
    
    board.candidates = set()
    for i, (q, r) in enumerate(board.coords):
        for dq, dr in DIRECTIONS:
            cq, cr = q + dq, r + dr
            if (cq, cr) not in board.index:
                count = sum(1 for ddq, ddr in DIRECTIONS if (cq + ddq, cr + ddr) in board.index)
                if 2 <= count <= 4:
                    board.candidates.add((cq, cr))
    
    board.neighbour_count = [0] * 19
    for i, (q, r) in enumerate(board.coords):
        board.neighbour_count[i] = sum(1 for dq, dr in DIRECTIONS if (q+dq, r+dr) in board.index)

    return board
    

def get_best_move(data, player, time_limit=2.0, c=2.0, policy='random', num_workers=4):
    board = create_board(data)
    board_state = board.save()
    pool = get_pool()
    phase = 0

    args = (board_state, player, time_limit, c, phase, policy)
    results = pool.map(run_worker, [args] * num_workers)
    
    merged = {}
    for result in results:
        if isinstance(result, tuple):
            result = result[0]
        for move, visits in result.items():
            merged[move] = merged.get(move, 0) + visits
    
    best_move = max(merged, key=merged.get)
    tk_move = [list(board.coords[best_move[1]]), STR_DIRECTIONS[best_move[2]]]
    board.move_token(best_move[1], best_move[2])

    phase = 1
    board_state = board.save()
    args = (board_state, player, time_limit, c, phase, policy)
    results = pool.map(run_worker, [args] * num_workers)
    
    merged = {}
    for result in results:
        if isinstance(result, tuple):
            result = result[0]
        for move, visits in result.items():
            merged[move] = merged.get(move, 0) + visits
    
    best_move = max(merged, key=merged.get)
    dsc_move = [list(board.coords[best_move[1]]), list(best_move[2])]

    #tk_move -> [[q,r], dir], dsc_move -> [[q1,r1], [q2, r2]], q + r + s = 0, so s = -q -r
    tk_coords = tk_move[0]

    dsc_move_old = dsc_move[0]

    dsc_move_new = dsc_move[1]

    tkq, tkr = tk_coords
    tks = -tkq-tkr
    doq, dor = dsc_move_old
    dos = -doq-dor
    dnq, dnr = dsc_move_new
    dns = -dnq-dnr
    
    return f"mp {tkq},{tkr},{tks} {tk_move[1]}, mb {doq},{dor},{dos} {dnq},{dnr},{dns};"


def recv_full_message(conn):
    buffer = b""
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            break
        buffer += chunk
        if b"\n" in buffer:
            message, _ = buffer.split(b"\n", 1)
            return message.decode("utf-8")
    raise ConnectionError("Connection closed before a complete message arrived")


# Data we receive -> coords, red_coords, black_coords, last_moved, colour, player_socketId
def handle_client(conn):
    try:
        raw = recv_full_message(conn)
        request = json.loads(raw)

        data = {
            'coords': [tuple(c) for c in request['coords']],
            'red_coords': [tuple (c) for c in request['red_coords']],
            'black_coords': [tuple (c) for c in request['black_coords']],
            'last_moved': tuple(request['last_moved']) if request['last_moved'] else None,
            'colour': request['colour']
        }

        int_col = RED if data['colour'] == 'r' else BLACK

        best_move = get_best_move(data, player=int_col)
        conn.sendall((best_move + '\n').encode())
    except Exception as e:
        conn.sendall((json.dumps({'error': str(e)}) + '\n').encode())
    finally:
        conn.close()

def get_pool():
    global _pool
    if _pool is None:
        _pool = Pool(4)
    return _pool

if __name__ == "__main__":
    _pool = Pool(4)

    HOST = '0.0.0.0'
    PORT = 5000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print(f"Listening on {PORT}")

        while True:
            conn, addr = s.accept()
            handle_client(conn)