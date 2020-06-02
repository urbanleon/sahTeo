var pieces = document.querySelectorAll("img");
var squares = document.querySelectorAll("div .square");

var pos = document.getElementById("position");

var chess = new Chess();

// let bestMove = document.getElementById("bestMove");

//FIXME: black captures white
//FIXME: vertical movements not caught because only checks posX for clearInterval
//FIXME: angle sometimes incorrect
function moveBot(move) {
    let mvFrom = move.substring(0,2);
    let mvTo = move.substring(2,4);
    // bestMove.textContent = 'from: ' + mvFrom + ' to: ' + mvTo;

    //get elements with id's of sqfrom and sqto
    let sqFrom = document.getElementById(mvFrom);
    let sqTo = document.getElementById(mvTo);
    let mvPiece = sqFrom.firstChild;

    //get positions of those elements
    let startPos = sqFrom.getBoundingClientRect();
    let endPos = sqTo.getBoundingClientRect();

    //set element zIndex to 1
    mvPiece.style.zIndex = 1;

    //calculate angle between elements
    let diffX = endPos.x - startPos.x;
    let diffY = endPos.y - startPos.y;
    let angle = Math.atan(diffY / diffX);
    if (diffX < 0 || (diffX < 0 && diffY < 0)) {
        angle = Math.PI - angle * -1;
    }
    // console.log('x,y,angle: ' + diffX + ' ' + diffY + ' ' + (angle * 180 / Math.PI));
    //animate piece
    let id = setInterval(frame, 15);
    let speed = 30;
    let posX = 0;
    let posY = 0;
    function frame() {
        if (((diffX < 0) && posX <= diffX) || ((diffX > 0) && posX >= diffX) || ((diffY < 0) && posY <= diffY) || ((diffY > 0) && posY >= diffY)) {
            mvPiece.style.left = diffX + 'px';
            mvPiece.style.top = diffY + 'px';
            clearInterval(id);
            if (sqTo.firstChild) {
                sqTo.removeChild(sqTo.firstChild);
            }
            sqTo.append(mvPiece);
            mvPiece.style.left = "";
            mvPiece.style.top = "";
            chess.move({from: mvFrom, to: mvTo});
            if (chess.in_checkmate()) {
                document.getElementById("result").textContent = "CHECKMATE";
            }
            // document.getElementById("fen").textContent = chess.ascii();
        } else {
            posX += speed * Math.cos(angle);
            posY += speed * Math.sin(angle);
            // document.getElementById("pos").textContent = Math.floor(posX) + ' ' + Math.floor(posY);
            mvPiece.style.left = posX + 'px';
            mvPiece.style.top = posY + 'px';
        }
    }
}

//set up api
let xhr = new XMLHttpRequest();
xhr.onload = function() {
    let move = xhr.responseText
    // bestMove.textContent = move;
    moveBot(move);
}

//initalize pieces to be dragged and dropped
for (let i = 0; i < pieces.length; ++i) {  

    //disable native drag event
    pieces[i].ondragstart = function() {
        return false;
    }

    //create event handlers for custom drag events
    pieces[i].onmousedown = function(event) {
        this.style.position = 'absolute';
        this.style.zIndex = 1000;
        document.body.append(this);
        
        moveAt(event.pageX, event.pageY, pieces[i]);

        function onMouseMove(event) {
            moveAt(event.pageX, event.pageY, pieces[i]);
        }

        document.addEventListener('mousemove', onMouseMove);

        let currSquare = maxOverlap(this, potentialDrops(this));
        let validMoves = getValidMoves(this);

        this.onmouseup = function() {
            dropPiece(this, currSquare, validMoves);
            document.removeEventListener('mousemove', onMouseMove);
            this.onmouseup = null;
        };

        highlightValidMoves(this);
    };
}

function getValidMoves(piece) {
    let currSquare = maxOverlap(piece, potentialDrops(piece));
    let tempMove = {square: currSquare.id, verbose: true};
    let validPositions = chess.moves(tempMove);
    return validPositions;
}

function highlightValidMoves(piece) {
    let validMoves = getValidMoves(piece);

    for (let j = 0; j < squares.length; j++) {
        for (let k = 0; k < validMoves.length; k++) {
            if (squares[j].id === validMoves[k].to) {
                let highlight = squares[j].classList[0] === "black" ? "validBlack" : "validWhite";
                squares[j].classList.add(highlight);
            }
        }
    }
}

//image follows position of cursor
function moveAt(pageX, pageY, obj) {
    obj.style.left = pageX - obj.offsetWidth / 2 + 'px';
    obj.style.top = pageY - obj.offsetHeight / 2 + 'px';
}

//detects if two objects are overlapping returns boolean
function overlap(img, square) {
    let imgRect = img.getBoundingClientRect();
    let squareRect = square.getBoundingClientRect();

    return !(imgRect.right <= squareRect.left ||
             imgRect.left >= squareRect.right ||
             imgRect.bottom <= squareRect.top ||
             imgRect.top >= squareRect.bottom);
}

//find the overlap amount between the image and a given square
//sum across both dimensions
function sumOverlap(img, square) {
    let imgRect = img.getBoundingClientRect();
    let squareRect = square.getBoundingClientRect();

    //minus 1 because shared borders cause ambiguous click, which caused
    //bottom and right piece to replace adjacent piece of same color
    let left = Math.abs((squareRect.left - 1) - imgRect.left);
    let top = Math.abs((squareRect.top - 1) - imgRect.top);

    return left + top;
}

//finds which square a piece overlaps the most with
function maxOverlap(img, squares) {
    let minIndex = 0;
    let minSum = 9999;
    for (let i = 0; i < squares.length; i++) {
        let temp = sumOverlap(img, squares[i])
        if (temp < minSum) {
            minSum = temp;
            minIndex = i;
        }
    }

    return squares[minIndex];
}

//returns the squares that the current piece
//overlaps
function potentialDrops(obj) {
    let dropZones = [];
    for (let i = 0; i < squares.length; i++) {
        if (overlap(obj, squares[i])) {
            dropZones.push(squares[i]);
        }
    }
    
    return dropZones;
}

//FIXME: check color of promoted piece
function checkSpecialMoves(currSquare, chosenMove, dropSquare, piece) {
    let tempMove = {from: currSquare.id, to: dropSquare};
    if (chosenMove) {
        let isPromotion = chosenMove.flags.indexOf('p');
        let isEnPassant = chosenMove.flags.indexOf('e');
        if (isPromotion != -1) {
            tempMove = {from: currSquare.id, to: dropSquare, promotion: 'q'};
            piece.src = "http://images.chesscomfiles.com/chess-themes/pieces/neo/75/wq.png";
        }
        if (isEnPassant != -1) {
            let capturedId = chosenMove.to[0] + chosenMove.from[1];
            let capturedSquare = document.getElementById(capturedId);
            capturedSquare.removeChild(capturedSquare.firstChild);
        }
    }
    return tempMove;
}

function removeHighlights() {
    for (let i = 0; i < squares.length; i++) {
        squares[i].classList.remove("validWhite");
        squares[i].classList.remove("validBlack");        
    }
}

function resetPosition(piece) {
    piece.style.top = 0;
    piece.style.left = 0;
}

function revertPosition(isValid, closestDrop, currSquare, piece) {
    let dropSquare = currSquare.id;
    if (isValid) {
        //if an image is already present, this indicates a capture
        if (closestDrop.firstChild) {
            closestDrop.removeChild(closestDrop.firstChild);
        }
        closestDrop.append(piece);
        dropSquare = closestDrop.id;
    }
    else {
        if (currSquare.firstChild) {
            currSquare.removeChild(currSquare.firstChild);
        }
        currSquare.append(piece);
    }
    return dropSquare
}

function sendFen() {
    xhr.open("POST", "http://127.0.0.1:8000/", true);
    let fen = chess.fen();
    xhr.send(JSON.stringify({value: fen}));
}

//handler for dropping a piece on a square
function dropPiece(piece, currSquare, validMoves) {
    let possibleDrops = potentialDrops(piece);
    let dropSquare = currSquare.id;
    let chosenMove = null;
    
    if (possibleDrops.length != 0) {
        let closestDrop = maxOverlap(piece, possibleDrops);
        let isValid = false;

        for (let i = 0; i < validMoves.length; i++) {
            if (closestDrop.id === validMoves[i].to) {
                isValid = true;
                //save chosen move to check for promotion
                chosenMove = validMoves[i];
            }
        }

        //return to original square if invalid
        dropSquare = revertPosition(isValid, closestDrop, currSquare, piece);
        
    }
    else {
        currSquare.append(piece);
    }

    resetPosition(piece);
    removeHighlights();

    let tempMove = checkSpecialMoves(currSquare, chosenMove, dropSquare, piece);

    chess.move(tempMove);

    if (chess.turn() == 'b') {
        sendFen();
    }
    else {
        bestMove.textContent = "";
    }


    if (chess.in_checkmate()) {
        document.getElementById("result").textContent = "CHECKMATE";
    }
}
