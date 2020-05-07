var pieces = document.querySelectorAll("img");
var squares = document.querySelectorAll("div .square");

var chess = new Chess();

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

        pieces[i].onmouseup = function() {
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

    let left = Math.abs(squareRect.left - imgRect.left);
    let top = Math.abs(squareRect.top - imgRect.top);

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

//handler for dropping a piece on a square
//FIXME: push move onto chess move stack
function dropPiece(piece, currSquare, validMoves) {
    let possibleDrops = potentialDrops(piece);
    console.log(validMoves);
    if (possibleDrops.length != 0) {
        let closestDrop = maxOverlap(piece, possibleDrops);
        let isValid = false;

        for (let i = 0; i < validMoves.length; i++) {
            if (closestDrop.id === validMoves[i].to) {
                isValid = true;
            }
        }
        console.log("isValid: " + isValid);
        if (isValid) {
            closestDrop.append(piece);
        }
        else {
            currSquare.append(piece);
        }
        
        piece.style.top = 0;
        piece.style.left = 0;
    }
    //remove highlights
    for (let i = 0; i < squares.length; i++) {
        squares[i].classList.remove("validWhite");
        squares[i].classList.remove("validBlack");        
    }
}