export function getValidMoves(board, pieceCoord) {

    if(!pieceCoord) return [];

    const [x, y, z] = pieceCoord;
    const key = `${x},${y},${z}`;

    if (!board[key]) return [];
    if (board[key].occupation === "N") return [];

    const directions = {
        "ur" : [1, 0, -1],
        "mr" : [1, -1, 0],
        "dr" : [0, -1, 1],
        "dl" : [-1, 0, 1],
        "ml" : [-1, 1, 0],
        "ul" : [0, 1, -1]
    };

    const validMoves = [];

    for (const dirKey in directions) {
        const dir = directions[dirKey];
        let delta = 1;
        let lastValid = null;

        while(true) {
            const newX = x + dir[0] * delta;
            const newY = y + dir[1] * delta;
            const newZ = z + dir[2] * delta;

            const key = `${newX},${newY},${newZ}`;

            if(!(key in board))break;
            if(board[key].occupation !== "N")break;

            lastValid = key;
            delta++;
        }
        if (lastValid){
            validMoves.push(lastValid);
        }
    }

    return validMoves;
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

export function getPiecesToMove(board){
    let canMovePiecesKeys = []

    for (const key in board){
        if (neighbourCount(board[key].coord, board) < 5 && board[key].occupation === "N" && !board[key].just_moved){
            canMovePiecesKeys.push(key);
        }
    }
    return canMovePiecesKeys
}

export function getPossibleBoardMoves(board, removedPiece){
    const directions = [
        [1, 0, -1], [1, -1, 0], [0, 1, -1], [0, -1, 1], [-1, 0, 1], [-1, 1, 0]
    ];

    const [x, y, z] = removedPiece;

    const removedPieceKey = `${x},${y},${z}`;

    const possibleMoves = new Set();

    for (const key in board){
        const [x, y, z] = board[key].coord;

        if(key === removedPieceKey) continue;

        for (const [dx, dy, dz] of directions){

            const newX = x + dx;
            const newY = y + dy;
            const newZ = z + dz;

            const neighbourKey = `${newX},${newY},${newZ}`;

            if(neighbourKey in board)continue;

            let neighbourCount = 0;

            for (const [dx2, dy2, dz2] of directions) {
                const checkKey = `${newX + dx2},${newY + dy2},${newZ + dz2}`;

                if(checkKey in board && checkKey !== removedPieceKey){
                    neighbourCount++;
                }
            }
            
            if(neighbourCount >= 2){
                possibleMoves.add(neighbourKey);
            }
        }
    }

    return Array.from(possibleMoves);
}

export function checkWin(board, occupation){
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