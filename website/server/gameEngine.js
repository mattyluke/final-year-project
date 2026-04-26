module.exports = { generateBoardPieces, parseMove, checkWin };

function generateBoardPieces() {
    const board = {};

    for (let x = -2; x <= 2; x++) {
        for (let y = -2; y <= 2; y++){
            for (let z = -2; z <= 2; z++){
                if (x + y + z == 0){

                    let occupation = "N";

                    if (
                        (x === 2 && y === 0 && z === -2) ||
                        (x === 0 && y === -2 && z === 2) || 
                        (x === -2 && y === 2 && z === 0)
                    ) {
                        occupation = "r";
                    }

                    if (
                        (x === 0 && y === 2 && z === -2) ||
                        (x === 2 && y === -2 && z === 0) || 
                        (x === -2 && y === 0 && z === 2)
                    ) {
                        occupation = "b";
                    }

                    const key = `${x},${y},${z}`;

                    board[key] = {
                    coord: [x, y, z],
                    occupation: occupation,
                    just_moved: false
                    };
                }
            }
        }
    }

    return board;
}

function movePlayer(board, piece, direction){

    const [x, y, z] = piece;
    if(board[`${x},${y},${z}`].occupation === "N") return;

    const directions = {
        "ur" : [1, 0, -1],
        "mr" : [1, -1, 0],
        "dr" : [0, -1, 1],
        "dl" : [-1, 0, 1],
        "ml" : [-1, 1, 0],
        "ul" : [0, 1, -1]
    }

    let delta = 1;
    let lastValid = null;

    const dir = directions[direction]
    if (!dir) return;

    while (true) {

        const newX = x + dir[0] * delta;
        const newY = y + dir[1] * delta;
        const newZ = z + dir[2] * delta;

        const key = `${newX},${newY},${newZ}`;

        if (!(key in board)) break;
        if (board[key].occupation !== "N") break;

        lastValid = key;
        delta++;
    }

    if (lastValid) {
        board[lastValid].occupation = board[`${x},${y},${z}`].occupation;
        board[`${x},${y},${z}`].occupation = "N";
        checkWin(board, board[lastValid].occupation);
    }
}

function neighbourCount(piece, board){
    const directions = [[1, 0, -1], [1, -1, 0], [0, 1, -1], [0, -1, 1], [-1, 0, 1], [-1, 1, 0]];
    const [x, y, z] = piece;
    let count = 0;

    for (const [dx, dy, dz] of directions) {
        const key = `${x + dx},${y + dy},${z + dz}`;
        if(key in board){
            count ++;
        }
    }

    return count;
}

function movePiece(board, piece, new_coord){
    const key = `${piece[0]},${piece[1]},${piece[2]}`;
    if(!(key in board)) return;

    if(board[key].occupation !== "N") return;

    if(neighbourCount(piece, board) > 4) return;

    if(neighbourCount(new_coord, board) < 2) return;

    delete board[key];

    for (const key in board) {
        const tile = board[key];

        tile.just_moved = false;
    }

    const newKey = `${new_coord[0]},${new_coord[1]},${new_coord[2]}`;

    if(newKey in board) return;

    board[newKey] = {coord: new_coord, occupation: "N", just_moved: true};
}

function checkWin(board, occupation){
    const directions = [[1, 0, -1], [1, -1, 0], [0, 1, -1], [0, -1, 1], [-1, 0, 1], [-1, 1, 0]];

    for( const [key, tile] of Object.entries(board)){
        if (tile.occupation !== occupation) continue;

        const[x, y, z] = tile.coord;
        let neighbourCount = 0;

        for (const [dx, dy, dz] of directions){
            const neighbourKey = `${x + dx},${y + dy},${z + dz}`;

            if (neighbourKey in board && board[neighbourKey].occupation === occupation){
                neighbourCount ++;
            }
        }

        if(neighbourCount >= 2){
            return occupation;
        }
    }

    return "N";
}

function parseMove(board, move) {
    // We have an algebraic notation for the game: 'mp x,y,z dir, mb x1,y1,z1 x2,y2,z2;' where xyz are integers.
    // However wins have a specific notation: 'mp x,y,z dir;' due to ending half way through a players full turn when a winning move is made.

    const str = move.split(" ");
    str[2] = str[2].substring(0, str[2].length - 1);
    if (str.length > 3) str[5] = str[5].substring(0, str[5].length - 1);
    

    if(str[0] !== "mp") return;
    if(str.length > 3 && str[3] !== "mb") return;

    const player_piece = str[1].split(",").map(Number);

    if (str.length <= 3) {movePlayer(board, player_piece, str[2]); return board;}

    const board_piece_pos_1 = str[4].split(",").map(Number);
    const board_piece_pos_2 = str[5].split(",").map(Number);

    movePlayer(board, player_piece, str[2]);
    movePiece(board, board_piece_pos_1, board_piece_pos_2);

    return board;
}