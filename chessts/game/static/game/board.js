const pieces = document.querySelectorAll("img");
const squares = document.querySelectorAll("div .square");
const board = document.querySelector('.board');
const pos = document.getElementById("position");
const xhr = new XMLHttpRequest();
const chess = new Chess();

window.onload = resizePieces();
window.addEventListener('resize', resizePieces);

//set up api
xhr.onload = function() {
    let move = xhr.responseText;
    moveBot(move);
}

initPieces();

function resizePieces() {
    let squareWidth = Math.round(squares[0].getBoundingClientRect().width);
    for (let i = 0; i < squares.length; i++) {
        if (squares[i].firstChild) {
            let currLink = squares[i].firstChild.src;
            let pieceType = currLink.substr(currLink.length - 6, currLink.length);
            let newLink = "https://images.chesscomfiles.com/chess-themes/pieces/neo/" + squareWidth + "/" + pieceType;
            squares[i].firstChild.src = newLink;
        }
    }
}

//if move is 5 chars long, then promotion
function moveBot(move) {
    console.log("moveBot: " + move)
    let mvFrom = move.substring(0,2);
    let mvTo = move.substring(2,4);

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
    //account for opposite directions
    if (diffX < 0 || (diffX < 0 && diffY < 0)) {
        angle = Math.PI - angle * -1;
    }

    //animate piece
    let id = setInterval(frame, 15);
    let speed = 30;
    let posX = 0;
    let posY = 0;

    function frame() {
        if (((diffX < 0) && posX + speed <= diffX) || ((diffX > 0) && posX + speed >= diffX) || 
            ((diffY < 0) && posY + speed <= diffY) || ((diffY > 0) && posY + speed >= diffY)) {
            mvPiece.style.left = diffX + 'px';
            mvPiece.style.top = diffY + 'px';
            clearInterval(id);
            checkCapture(sqTo, mvPiece);
            resetPosition(mvPiece);
            //FIXME: add promotion parameter to checkSpecialMoves()
            let tempMove = null;
            if (move.length === 5) {
                tempMove = chess.move({from: mvFrom, to: mvTo, promotion: 'q'});
            }
            else {
                tempMove = chess.move({from: mvFrom, to: mvTo});
            }
            checkSpecialMoves(mvFrom, tempMove, mvTo, mvPiece);
            checkEndGame();
        } else {
            posX += speed * Math.cos(angle);
            posY += speed * Math.sin(angle);
            mvPiece.style.left = posX + 'px';
            mvPiece.style.top = posY + 'px';
        }
    }

    document.getElementById('thinking').classList.remove('lds-grid');
}


//initalize pieces to be dragged and dropped
//FIXME: when playing white, do no enable black for dragging
function initPieces() {
    for (let i = 0; i < pieces.length; ++i) {  

        //disable native drag event
        pieces[i].ondragstart = function() {
            return false;
        }
        pieces[i].ontouchstart = function(event) {
            console.log("touch started");
            this.style.position = 'absolute';
            this.style.zIndex = 1;
            // this.style.cursor = 'grabbing';
            document.body.append(this);

            if (event.targetTouches.length <= 1) {
                moveAt(event.touches[0].pageX, event.touches[0].pageY, pieces[i]);
            } 
            else {
                onTouchUp();
            }

            window.addEventListener('touchend', onTouchUp);
            document.addEventListener('touchmove', onTouchMove);

            let currSquare = maxOverlap(this, potentialDrops(this));
            let validMoves = getValidMoves(this);
    
            function onTouchMove(event) {
                moveAt(event.touches[0].pageX, event.touches[0].pageY, pieces[i]);
            }
    
            function onTouchUp() {
                // pieces[i].style.cursor = 'grab';
                dropPiece(pieces[i], currSquare, validMoves);
                document.removeEventListener('touchmove', onTouchMove);
                window.removeEventListener('touchend', onTouchUp);
                console.log("touch ended");
            }
    
            highlightValidMoves(this);
        };
        //create event handlers for custom drag events
        pieces[i].onmousedown = function(event) {
            this.style.position = 'absolute';
            this.style.zIndex = 1;
            this.style.cursor = 'grabbing';
            document.body.append(this);
    
            moveAt(event.pageX, event.pageY, pieces[i]);
    
            window.addEventListener('mouseup', onMouseUp);
            document.addEventListener('mousemove', onMouseMove);
    
            let currSquare = maxOverlap(this, potentialDrops(this));
            let validMoves = getValidMoves(this);
    
            function onMouseMove(event) {
                moveAt(event.pageX, event.pageY, pieces[i]);
            }
    
            function onMouseUp() {
                pieces[i].style.cursor = 'grab';
                dropPiece(pieces[i], currSquare, validMoves);
                document.removeEventListener('mousemove', onMouseMove);
                window.removeEventListener('mouseup', onMouseUp);
            }
    
            highlightValidMoves(this);
        };
    }
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


//currSquare (FROM square): square element corresponding to original position
//chosenMove (MOVE object): chessjs move object
//dropSquare (TO square): id (string) of square to be dropped, whether chosenMove or currSquare.id
//piece: img element
function checkSpecialMoves(currSquareId, chosenMove, dropSquare, piece) {
    let tempMove = {from: currSquareId, to: dropSquare};
    if (chosenMove) {
        let isPromotion = chosenMove.flags.indexOf('p');
        let isEnPassant = chosenMove.flags.indexOf('e');
        let isKCastle = chosenMove.flags.indexOf('k');
        let isQCastle = chosenMove.flags.indexOf('q');
        if (isPromotion != -1) {
            let squareWidth = Math.round(squares[0].getBoundingClientRect().width);
            tempMove = {from: currSquareId, to: dropSquare, promotion: 'q'};
            if (chosenMove.color === 'w') {
                piece.src = "https://images.chesscomfiles.com/chess-themes/pieces/neo/" + squareWidth + "/wq.png";
            }
            else {
                piece.src = "https://images.chesscomfiles.com/chess-themes/pieces/neo/" + squareWidth + "/bq.png";
            }
        }
        if (isEnPassant != -1) {
            let capturedId = chosenMove.to[0] + chosenMove.from[1];
            let capturedSquare = document.getElementById(capturedId);
            capturedSquare.removeChild(capturedSquare.firstChild);
        }
        if (isKCastle != -1) {
            chosenMove.color === 'w' ? moveBot('h1f1') : moveBot('h8f8');
        }
        if (isQCastle != -1) {
            chosenMove.color === 'w' ? moveBot('a1d1') : moveBot('a8d8');
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
    piece.style.top = "";
    piece.style.left = "";
}

function revertPosition(isValid, closestDrop, currSquare, piece) {
    let dropSquare = currSquare.id;
    if (isValid) {
        checkCapture(closestDrop, piece);
        dropSquare = closestDrop.id;
    }
    else {
        currSquare.append(piece);
    }
    return dropSquare;
}

function checkCapture(square, newPiece) {
    if (square.firstChild) {
        square.removeChild(square.firstChild);
    }
    square.append(newPiece);
}

function checkEndGame() {
    if (chess.in_checkmate()) {
        let gameResult = chess.turn() == 'b' ? "WHITE wins by" : "BLACK wins by";
        document.getElementById("winner").innerHTML = gameResult;
        document.getElementById("endGameType").textContent = "CHECKMATE";
    } 
    else if (chess.in_threefold_repetition()) {
        document.getElementById("endGameType").innerHTML = "DRAW";
        document.getElementById("endBy").textContent = "Threefold Repetition";
    }
    else if (chess.in_stalemate()) {
        document.getElementById("endGameType").innerHTML = "DRAW";
        document.getElementById("endBy").textContent = "Stalemate";
    }
    else if (chess.insufficient_material()) {
        document.getElementById("endGameType").innerHTML = "DRAW";
        document.getElementById("endBy").textContent = "Insufficient Material";
    }
    else if (chess.in_draw()) {
        document.getElementById("endGameType").textContent = "DRAW";
    }
    if (chess.game_over()) {
        document.getElementById('thinking').classList.remove('lds-grid');
    }
}

function sendFen() {
    xhr.open("POST", document.URL, true);
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

    let tempMove = checkSpecialMoves(currSquare.id, chosenMove, dropSquare, piece); 

    chess.move(tempMove);

    if (chess.turn() == 'b') {
        sendFen();
        document.getElementById('thinking').classList.add('lds-grid');
    }

    checkEndGame();
}
