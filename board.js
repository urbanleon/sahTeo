var pieces = document.querySelectorAll("img");
var squares = document.querySelectorAll("div .square");

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

        pieces[i].onmouseup = function() {
            // dropPiece(this);
            setTimeout(dropPiece, 50, this);
            document.removeEventListener('mousemove', onMouseMove);
            this.onmouseup = null;
        };
    };
}

function moveAt(pageX, pageY, obj) {
    obj.style.left = pageX - obj.offsetWidth / 2 + 'px';
    obj.style.top = pageY - obj.offsetHeight / 2 + 'px';
}

function overlap(img, square) {
    let imgRect = img.getBoundingClientRect();
    let squareRect = square.getBoundingClientRect();

    return !(imgRect.right < squareRect.left ||
             imgRect.left > squareRect.right ||
             imgRect.bottom < squareRect.top ||
             imgRect.top > squareRect.bottom);
}

function sumOverlap(img, square) {
    let imgRect = img.getBoundingClientRect();
    let squareRect = square.getBoundingClientRect();

    let left = Math.abs(squareRect.left - imgRect.left);
    let top = Math.abs(squareRect.top - imgRect.top);

    return left + top;
}

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

function dropPiece(obj) {
    let possible_drops = [];

    for (let i = 0; i < squares.length; i++) {
        if (overlap(obj, squares[i])) {
            possible_drops.push(squares[i]);
            // squares[i].classList.add("possibleDrop");
        }
    }

    let closestDrop = maxOverlap(obj, possible_drops);

    closestDrop.append(obj);

    obj.style.top = 0;
    obj.style.left = 0;
}