import { getValidMoves, getPiecesToMove, getPossibleBoardMoves, checkWin } from './clientLogic.js';
import { Application, Graphics, Container, GlProgram, Filter } from 'https://unpkg.com/pixi.js@8.13.2/dist/pixi.mjs';
import { onGameStarted, sendMove, onGameUpdated, sendWin, onGameOver } from "./gameHandling.js";

let hexGraphics = {};
const hexSize = 60;
let currentMove = {
        pieceFrom: null,
        pieceTo: null,
        boardFrom: null,
        boardTo: null
    }

let myColor = null;
let myTurn = null;

function cubeToPixel(cubeX, cubeZ, size){
    return {
        x: size * (Math.sqrt(3) * cubeX + Math.sqrt(3)/2 * cubeZ),
        y: size * (3/2 * cubeZ)
    };
}


function showHighlights(board, moveKeys, highlightLayer){
    highlightLayer.removeChildren();

    moveKeys.forEach(key => {
        const [x, y, z] = board[key].coord;
        const pos = cubeToPixel(x, z, hexSize);

        const highlight = new Graphics()
        .regularPoly(
            pos.x,
            pos.y,
            hexSize,
            6
        )
        .fill({color:0x00ff00, alpha: 0.4});

        highlightLayer.addChild(highlight);
    }
    );
}


function getDirection(from, to){

    const directions = {
        "1,0,-1": "ur",
        "1,-1,0": "mr",
        "0,-1,1": "dr",
        "-1,0,1": "dl",
        "-1,1,0": "ml",
        "0,1,-1": "ul"
    }

    const dx = to[0] - from[0];
    const dy = to[1] - from[1];
    const dz = to[2] - from[2];

    const len = Math.max(Math.abs(dx), Math.abs(dy), Math.abs(dz));

    const key = `${dx/len},${dy/len},${dz/len}`;
    return directions[key];
}


function buildMove(pieceFrom, pieceTo, boardFrom, boardTo){
    const dir = getDirection(pieceFrom, pieceTo);
    return `mp ${pieceFrom.join(",")} ${dir}, mb ${boardFrom.join(",")} ${boardTo.join(",")};`;
}


function createPiece(board, piece, color, highlightLayer, pieceLayer, gameId) {
    const hexColor = color === "r" ? 0xff0000 : 0x000000;
    const [x, y, z] = piece.coord;
    const pos = cubeToPixel(x, z, hexSize);

    const circle = new Graphics().circle(0, 0, hexSize * 0.4).fill({ color: hexColor });
    circle.x = pos.x;
    circle.y = pos.y;

    if (myTurn && piece.occupation === myColor) {
        circle.eventMode = 'static';
    circle.cursor = 'pointer';

    circle
        .on('pointerdown', () => {
            circle.dragging = true;
            currentMove.pieceFrom = piece.coord;
            circle.originalPosition = { x: circle.x, y: circle.y };
            circle.possibleMoves = getValidMoves(board, piece.coord);
            showHighlights(board, circle.possibleMoves, highlightLayer);
        })
        .on('globalpointermove', (event) => {
            if (!circle.dragging) return;
            const pos = event.getLocalPosition(circle.parent);
            circle.position.set(pos.x, pos.y);
        })
        .on('pointerup', () => {
            circle.dragging = false;
            circle.alpha = 1;
            let snapped = false;
            let winner = "N";

            for (const key of circle.possibleMoves) {
                const [x, y, z] = board[key].coord;
                const tilePos = cubeToPixel(x, z, hexSize);
                const dx = circle.x - tilePos.x;
                const dy = circle.y - tilePos.y;

                if (Math.sqrt(dx * dx + dy * dy) < hexSize * 0.8) {
                    circle.x = tilePos.x;
                    circle.y = tilePos.y;
                    currentMove.pieceTo = board[key].coord;

                    board[key].occupation = piece.occupation;
                    board[piece.coord.join(',')].occupation = "N";

                    snapped = true;
                    const winner = checkWin(board, myColor);
                    if (winner != "N") {
                        pieceLayer.addChild(circle);
                        const move = `mp ${currentMove.pieceFrom.join(",")} ${getDirection(currentMove.pieceFrom, currentMove.pieceTo)};`;
                        sendWin(move, myColor);
                    }
                    break;
                }
            }

            if (snapped && winner === "N") movePiece(board, highlightLayer, gameId);
            else if (circle.originalPosition) {
                circle.x = circle.originalPosition.x;
                circle.y = circle.originalPosition.y;
                highlightLayer.removeChildren();
            }
        })
        .on('pointerupoutside', () => {
            circle.dragging = false;
            circle.alpha = 1;
            highlightLayer.removeChildren();
        });
    }

    pieceLayer.addChild(circle);
}


function renderBoard(board, boardLayer, highlightLayer, pieceLayer, gameId) {

    for (const key in board) {
        const piece = board[key];
        const [x, y, z] = piece.coord;

        const pos = cubeToPixel(x, z, hexSize);

        const hex = new Graphics()
        .regularPoly(
            0,
            0,
            hexSize,
            6
        )
        .stroke({
            width:4,
            color: 0x000000
        })
        .fill({
            color:0xffffff
        });

        hex.x = pos.x;
        hex.y = pos.y;

        boardLayer.addChild(hex);
        hexGraphics[key] = hex;

        if (piece.occupation !== "N" && myTurn && piece.occupation === myColor) {
            createPiece(board, piece, piece.occupation, highlightLayer, pieceLayer, gameId);
        } else if (piece.occupation !== "N"){
            createPiece(board, piece, piece.occupation, highlightLayer, pieceLayer, gameId)
        }
    }
}


function renderPossibleBoardShapes(board, highlightLayer, futurePieces) {
    highlightLayer.removeChildren();

    futurePieces.forEach(key => {
        const [x, y, z] = key.split(',').map(Number);
        const pos = cubeToPixel(x, z, hexSize);

        const highlight = new Graphics()
        .regularPoly(
            pos.x,
            pos.y,
            hexSize,
            6
        )
        .fill({color:0x0000ff, alpha: 0.4});

        highlightLayer.addChild(highlight);
    }
    );
}


function updateHexColor(hex, color) {
    const currentX = hex.x;
    const currentY = hex.y;

    hex.clear()
        .regularPoly(0, 0, hexSize, 6)
        .fill({ color })
        .stroke({ width: 2, color: 0x000000 });

    hex.x = currentX;
    hex.y = currentY;
}


function movePiece(board, highlightLayer, gameId) {
    highlightLayer.removeChildren();
    const piecesToMoveKeys = getPiecesToMove(board);
    highlightLayer.eventMode = 'none';

    piecesToMoveKeys.forEach(key => {

        const hex = hexGraphics[key];
        const [x, y, z] = key.split(',').map(Number);
        const pos = cubeToPixel(x, z, hexSize);

        hex.clear().regularPoly(0, 0, hexSize, 6)
        .fill({color:0xeedfaf}).stroke({width: 2, color: 0x000000});
        hex.x = pos.x;
        hex.y = pos.y;

        hex.eventMode = 'static';
        hex.cursor = 'pointer';
        hex.interactive = true;

        hex.on('pointerdown', (event) => {
            hex.dragging = true;
            hex.alpha = 0.7;
            
            hex.originalPosition = {
                x: hex.x,
                y: hex.y
            };

            const futurePieces = getPossibleBoardMoves(board, key.split(',').map(Number));
            renderPossibleBoardShapes(board, highlightLayer, futurePieces);
        })
        .on('globalpointermove', (event) => {
            if (!hex.dragging) return;

            const pos = event.getLocalPosition(hex.parent);
            hex.position.set(pos.x, pos.y);
        })
        .on('pointerup', () => {
            console.log("Hex final position:", hex.x, hex.y);
            hex.dragging = false;
            hex.alpha = 1;

            let snapped = false;

            const futurePieces = getPossibleBoardMoves(board, key.split(',').map(Number));

            let newPosition = {
                x: null,
                y: null,
            }

            for (const moveKey of futurePieces){
                const [x,y,z] = moveKey.split(',').map(Number);
                const tilePos = cubeToPixel(x,z, hexSize);

                const stageX = tilePos.x;
                const stageY = tilePos.y;

                const dx = hex.x - stageX;
                const dy = hex.y - stageY;

                const distance = Math.sqrt(dx * dx + dy * dy);
                console.log(distance);

                if (distance < hexSize * 0.8){
                    hex.x = stageX;
                    hex.y = stageY;

                    newPosition.x = hex.x;
                    newPosition.y = hex.y;

                    snapped = true;
                    currentMove.boardFrom = key.split(',').map(Number);
                    currentMove.boardTo = moveKey.split(',').map(Number);
                    break;
                }
            }

            if (snapped) {
                for (const key of piecesToMoveKeys) {
                    const hex = hexGraphics[key];
                    if (!hex) continue;

                    updateHexColor(hex, 0xffffff);

                    const move = buildMove(currentMove.pieceFrom, currentMove.pieceTo, currentMove.boardFrom, currentMove.boardTo);
                    sendMove(move);
                }
            }

            if (!snapped && hex.originalPosition) {
                hex.x = hex.originalPosition.x;
                hex.y = hex.originalPosition.y;
            }
            highlightLayer.removeChildren();
        });
    });
}


export function createBackgroundShader(app) {

    // Fragment shader from https://www.shadertoy.com/view/WtdXR8

  const fragmentShader = `
    precision highp float;

uniform float uTime;
varying vec2 vTextureCoord;

vec3 palette(float t) {
  vec3 colors[6];
  colors[0] = vec3(0.0, 0.0, 0.5);       // navy
  colors[1] = vec3(0.4, 0.0, 0.6);       // purple
  colors[2] = vec3(0.8, 0.0, 0.0);       // red
  colors[3] = vec3(1.0, 0.75, 0.0);      // gold
  colors[4] = vec3(0.0, 0.0, 0.5);       // navy

  float scaled = mod(t, 1.0) * 5.0;
  int idx = int(scaled);
  float frac = scaled - float(idx);

  vec3 c0 = idx == 0 ? colors[0] : idx == 1 ? colors[1] : idx == 2 ? colors[2] : idx == 3 ? colors[3] : colors[4];
  vec3 c1 = idx == 0 ? colors[1] : idx == 1 ? colors[2] : idx == 2 ? colors[3] : idx == 3 ? colors[4] : colors[0];

  return mix(c0, c1, smoothstep(0.0, 1.0, frac));
}

void main() {
  vec2 resolution = vec2(${app.screen.width}.0, ${app.screen.height}.0);
  vec2 fragCoord = vTextureCoord * resolution;
  vec2 uv = (2.0 * fragCoord - resolution.xy) / min(resolution.x, resolution.y);

  for(float i = 1.0; i < 10.0; i++){
    uv.x += 0.6 / i * cos(i * 2.5 * uv.y + uTime);
    uv.y += 0.6 / i * cos(i * 1.5 * uv.x + uTime);
  }

  float brightness = 0.1 / abs(sin(uTime - uv.y - uv.x));
  vec3 color = palette(uTime * 1.9) * brightness;

  gl_FragColor = vec4(color, 1.0);
}
  `;

  const filter = new Filter({
    glProgram: GlProgram.from({
      vertex: `
        precision highp float;
        attribute vec2 aPosition;
        varying vec2 vTextureCoord;
        void main() {
          vTextureCoord = aPosition;
          gl_Position = vec4((aPosition * 2.0 - 1.0) * vec2(1.0, -1.0), 0.0, 1.0);
        }
      `,
      fragment: fragmentShader,
    }),
    resources: {
      timeUniforms: {
        uTime: { value: 0, type: 'f32' },
      }
    }
  });

  const background = new Graphics();
  background.rect(0, 0, app.screen.width, app.screen.height);
  background.fill(0x000000);
  background.filters = [filter];

  app.ticker.add((delta) => {
    filter.resources.timeUniforms.uniforms.uTime += delta.deltaTime * 0.0002;
  });

  return background;
}


export async function start() {
  const app = new Application();

  await app.init({
    resizeTo: window,
    autoDensity: true,
    antialias: true,
    background: 0x000000,
    preference: "webgl"
  });

  document.body.appendChild(app.canvas);

  const boardContainer = new Container();
  
  const boardLayer = new Container();
  const highlightLayer = new Container();
  const pieceLayer = new Container();

  boardContainer.addChild(boardLayer, highlightLayer, pieceLayer);

  const background = createBackgroundShader(app);

  app.stage.addChild(background, boardContainer);

  function centerBoard() {
    const bounds = boardContainer.getLocalBounds();

    boardContainer.pivot.set(
        bounds.x + bounds.width/2,
        bounds.y + bounds.height/2
    );

    boardContainer.position.set(
        app.screen.width/2,
        app.screen.height/2
    );
  }

  onGameStarted(({ gameId, game, color }) => {
    console.log("Game started", gameId);
    console.log("My color:", color);
    myColor = color;
    myTurn = myColor === game.currentTurn;
    renderBoard(game.board, boardLayer, highlightLayer, pieceLayer, gameId);
    centerBoard();
    if (color === "b") boardContainer.rotation = Math.PI;
  });


  onGameUpdated(({ game, gameId }) => {
    boardLayer.removeChildren();
    console.log("Update received.");
    highlightLayer.removeChildren();
    pieceLayer.removeChildren();
    hexGraphics = {};
    currentMove = {
        pieceFrom: null,
        pieceTo: null,
        boardFrom: null,
        boardTo: null
    };
    myTurn = myColor === game.currentTurn;
    renderBoard(game.board, boardLayer, highlightLayer, pieceLayer);
    centerBoard();
  })

  onGameOver(({ winner }) => {
    boardLayer.removeChildren();
    highlightLayer.removeChildren();
    pieceLayer.removeChildren();

    const text = document.createElement("h1");
    text.textContent = `${winner === "r" ? "Red" : "Black"} wins!`;
    text.style.cssText = "position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);color:white;font-size:4rem;text-align:center;white-space:nowrap;";
    document.body.appendChild(text);
  });



  app.renderer.on('resize', centerBoard);
}
