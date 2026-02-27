import { getValidMoves, getPiecesToMove, getPossibleBoardMoves} from './clientLogic.js';
import { Application, Graphics, Container, GlProgram, Filter } from 'https://unpkg.com/pixi.js@8.13.2/dist/pixi.mjs';

let hexGraphics = {};
const hexSize = 60;


/*const socket = io("http://localhost:3000");


socket.on("connect", () => {
    console.log("Connected:",socket.id);
});

socket.emit("start_game");

socket.on("waiting", (data) => {
    console.log(data.message);
});*/


function cubeToPixel(cubeX, cubeZ, size){
    return {
        x: size * (Math.sqrt(3) * cubeX + Math.sqrt(3)/2 * cubeZ),
        y: size * (3/2 * cubeZ)
    };
}


function generateBoardPieces() {
    const board = {};

    for (let x = -2; x <= 2; x++) {
        for (let y = -2; y <= 2; y++){
            for (let z = -2; z <= 2; z++){
                if (x + y + z == 0){

                    let occupation = "N";

                    if (
                        (x === -2 && y === 1 && z === 1) ||
                        (x === 1 && y === -2 && z === 1) || 
                        (x === 1 && y === 1 && z === -2)
                    ) {
                        occupation = "r";
                    }

                    if (
                        (x === -1 && y === 2 && z === -1) ||
                        (x === 2 && y === -1 && z === -1) || 
                        (x === -1 && y === -1 && z === 2)
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


function renderBoard(board, boardLayer, highlightLayer, pieceLayer) {

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

        if(piece.occupation === "r"){
            const circle = new Graphics().circle(0, 0, hexSize * 0.4).fill({color: 0xff0000});

            circle.x = pos.x;
            circle.y = pos.y;

            circle.eventMode = 'static';
            circle.cursor = 'pointer';
            
            circle
            .on('pointerdown', () => {
                circle.dragging = true;

                circle.originalPosition = {
                    x: circle.x,
                    y: circle.y
                }

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

                for (const key of circle.possibleMoves){
                    const [x, y, z] = board[key].coord;
                    const tilePos = cubeToPixel(x, z, hexSize);

                    const stageX = tilePos.x;
                    const stageY = tilePos.y;

                    const dx = circle.x - stageX;
                    const dy = circle.y - stageY;

                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < hexSize * 0.8){

                        circle.x = stageX;
                        circle.y = stageY;

                        snapped = true;
                        break;
                    }
                }

                if (snapped) {
                    movePiece(board, highlightLayer);
                }

                if (!snapped && circle.originalPosition){
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

            pieceLayer.addChild(circle);
        }

        if(piece.occupation === "b"){
            const circle = new Graphics().circle(0, 0, hexSize * 0.4).fill({color: 0x000000});

            circle.x = pos.x;
            circle.y = pos.y;

            circle.eventMode = 'static';
            circle.cursor = 'pointer';
            
            circle
            .on('pointerdown', () => {
                circle.dragging = true;

                circle.originalPosition = {
                    x: circle.x,
                    y: circle.y
                }

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

                for (const key of circle.possibleMoves){
                    const [x, y, z] = board[key].coord;
                    const tilePos = cubeToPixel(x, z, hexSize);

                    const stageX = tilePos.x;
                    const stageY = tilePos.y;

                    const dx = circle.x - stageX;
                    const dy = circle.y - stageY;

                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < hexSize * 0.8){

                        circle.x = stageX;
                        circle.y = stageY;

                        snapped = true;
                        break;
                    }
                }

                if (snapped) {
                    movePiece(board, highlightLayer);
                }

                if (!snapped && circle.originalPosition){
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

            pieceLayer.addChild(circle);
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


function movePiece(board, highlightLayer) {
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
                    break;
                }
            }

            if (snapped) {
                for (const key of piecesToMoveKeys) {
                    const hex = hexGraphics[key];
                    if (!hex) continue;

                    updateHexColor(hex, 0xffffff);
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
  colors[0] = vec3(0.0, 0.0, 0.0);       // black
  colors[1] = vec3(0.0, 0.0, 0.5);       // navy
  colors[2] = vec3(0.4, 0.0, 0.6);       // purple
  colors[3] = vec3(0.8, 0.0, 0.0);       // red
  colors[4] = vec3(1.0, 0.75, 0.0);      // gold
  colors[5] = vec3(0.0, 0.0, 0.0);       // black

  float scaled = mod(t, 1.0) * 5.0;
  int idx = int(scaled);
  float frac = scaled - float(idx);

  vec3 c0 = idx == 0 ? colors[0] : idx == 1 ? colors[1] : idx == 2 ? colors[2] : idx == 3 ? colors[3] : colors[4];
  vec3 c1 = idx == 0 ? colors[1] : idx == 1 ? colors[2] : idx == 2 ? colors[3] : idx == 3 ? colors[4] : colors[5];

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

  const board = generateBoardPieces();

  const boardContainer = new Container();
  
  const boardLayer = new Container();
  const highlightLayer = new Container();
  const pieceLayer = new Container();

  boardContainer.addChild(boardLayer, highlightLayer, pieceLayer);

  const background = createBackgroundShader(app);

  app.stage.addChild(background, boardContainer);

  renderBoard(board, boardLayer, highlightLayer, pieceLayer);

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

  centerBoard();

  app.renderer.on('resize', centerBoard);
}
