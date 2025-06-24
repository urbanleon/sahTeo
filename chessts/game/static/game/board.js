// board.js

function getCSRFToken() {
  return document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");
}

// Grab necessary elements
const pieces = document.querySelectorAll("img");
const squares = document.querySelectorAll("div .square");
const board = document.querySelector(".board");
const pos = document.getElementById("position");
const xhr = new XMLHttpRequest();
const chess = new Chess();

// Hook up resizePieces on load + resize
window.addEventListener("load", resizePieces);
window.addEventListener("resize", resizePieces);

// API callback
xhr.onload = function () {
  const move = xhr.responseText;
  moveBot(move);
};

initPieces();

/**
 * Resize each piece image to match square size
 */
function resizePieces() {
  if (!squares.length) return;
  const squareWidth = Math.round(squares[0].getBoundingClientRect().width);

  squares.forEach((square) => {
    const img = square.querySelector("img");
    if (!img) return;
    const pieceType = img.src.slice(-6);
    img.src = `https://images.chesscomfiles.com/chess-themes/pieces/neo/${squareWidth}/${pieceType}`;
  });
}

/**
 * Animate and execute bot move
 */
function moveBot(move) {
  console.log("moveBot:", move);
  const mvFrom = move.substring(0, 2);
  const mvTo = move.substring(2, 4);

  const sqFrom = document.getElementById(mvFrom);
  const sqTo = document.getElementById(mvTo);
  const mvPiece = sqFrom?.querySelector("img");

  // Guard: if no image found, bail and clear spinner
  if (!mvPiece) {
    console.error("moveBot failed: no <img> at", mvFrom);
    document.getElementById("thinking").classList.remove("lds-grid");
    return;
  }

  const startPos = sqFrom.getBoundingClientRect();
  const endPos = sqTo.getBoundingClientRect();

  mvPiece.style.zIndex = 1;
  const diffX = endPos.x - startPos.x;
  const diffY = endPos.y - startPos.y;
  const angle = Math.atan2(diffY, diffX);

  let posX = 0,
    posY = 0;
  const speed = 30;
  const id = setInterval(() => {
    const reachedX =
      (diffX < 0 && posX + speed <= diffX) ||
      (diffX > 0 && posX + speed >= diffX);
    const reachedY =
      (diffY < 0 && posY + speed <= diffY) ||
      (diffY > 0 && posY + speed >= diffY);
    if (reachedX || reachedY) {
      mvPiece.style.left = diffX + "px";
      mvPiece.style.top = diffY + "px";
      clearInterval(id);
      checkCapture(sqTo, mvPiece);
      resetPosition(mvPiece);

      const tempMove =
        move.length === 5
          ? chess.move({ from: mvFrom, to: mvTo, promotion: "q" })
          : chess.move({ from: mvFrom, to: mvTo });
      checkSpecialMoves(mvFrom, tempMove, mvTo, mvPiece);
      checkEndGame();
      // hide spinner after bot move completes
      document.getElementById("thinking").classList.remove("lds-grid");
    } else {
      posX += speed * Math.cos(angle);
      posY += speed * Math.sin(angle);
      mvPiece.style.left = posX + "px";
      mvPiece.style.top = posY + "px";
    }
  }, 15);
}

/**
 * Initialize drag & drop for pieces
 */
function initPieces() {
  // Set in Django context
  pieces.forEach((piece) => {
    const isWhite = piece.src.includes("/w");
    const isBlack = piece.src.includes("/b");

    // Skip pieces that don't belong to the player
    if (
      (playerColor === "white" && isBlack) ||
      (playerColor === "black" && isWhite)
    ) {
      return;
    }

    piece.ondragstart = () => false;

    // Touch support
    piece.ontouchstart = function (e) {
      const curr = maxOverlap(this, potentialDrops(this));
      const moves = getValidMoves(this);

      if (e.touches.length > 1) {
        onTouchUp();
        return;
      }

      this.style.position = "absolute";
      this.style.zIndex = 1;
      document.body.append(this);
      moveAt(e.touches[0].pageX, e.touches[0].pageY, this);

      window.addEventListener("touchend", onTouchUp);
      document.addEventListener("touchmove", onTouchMove);

      function onTouchMove(ev) {
        moveAt(ev.touches[0].pageX, ev.touches[0].pageY, piece);
      }

      function onTouchUp() {
        dropPiece(piece, curr, moves);
        clean();
      }

      function clean() {
        document.removeEventListener("touchmove", onTouchMove);
        window.removeEventListener("touchend", onTouchUp);
      }

      highlightValidMoves(this);
    };

    // Mouse support
    piece.onmousedown = function (e) {
      this.style.position = "absolute";
      this.style.zIndex = 1;
      this.style.cursor = "grabbing";
      document.body.append(this);
      moveAt(e.pageX, e.pageY, this);

      const curr = maxOverlap(this, potentialDrops(this));
      const moves = getValidMoves(this);

      window.addEventListener("mousemove", onMouseMove);
      window.addEventListener("mouseup", onMouseUp);

      function onMouseMove(ev) {
        moveAt(ev.pageX, ev.pageY, piece);
      }

      function onMouseUp() {
        piece.style.cursor = "grab";
        dropPiece(piece, curr, moves);
        clean();
      }

      function clean() {
        window.removeEventListener("mousemove", onMouseMove);
        window.removeEventListener("mouseup", onMouseUp);
      }

      highlightValidMoves(this);
    };
  });
}

// Additional helper functions unchanged...

function getValidMoves(piece) {
  const sq = maxOverlap(piece, potentialDrops(piece));
  return chess.moves({ square: sq.id, verbose: true });
}

function highlightValidMoves(piece) {
  const vm = getValidMoves(piece);
  squares.forEach((sq) =>
    vm.forEach((m) => {
      if (sq.id === m.to) {
        const cls = sq.classList.contains("black")
          ? "validBlack"
          : "validWhite";
        sq.classList.add(cls);
      }
    })
  );
}

function moveAt(x, y, o) {
  o.style.left = x - o.offsetWidth / 2 + "px";
  o.style.top = y - o.offsetHeight / 2 + "px";
}

function overlap(a, b) {
  const r1 = a.getBoundingClientRect(),
    r2 = b.getBoundingClientRect();
  return !(
    r1.right <= r2.left ||
    r1.left >= r2.right ||
    r1.bottom <= r2.top ||
    r1.top >= r2.bottom
  );
}

function sumOverlap(a, b) {
  const r1 = a.getBoundingClientRect(),
    r2 = b.getBoundingClientRect();
  return Math.abs(r2.left - 1 - r1.left) + Math.abs(r2.top - 1 - r1.top);
}

function potentialDrops(o) {
  return Array.from(squares).filter((sq) => overlap(o, sq));
}

function maxOverlap(a, arr) {
  let mi = 0,
    ms = Infinity;
  arr.forEach((s, i) => {
    const v = sumOverlap(a, s);
    if (v < ms) {
      ms = v;
      mi = i;
    }
  });
  return arr[mi];
}

function checkCapture(square, piece) {
  // Remove any existing piece(s) on the target square
  while (square.firstChild) {
    square.removeChild(square.firstChild);
  }
  // Append the moved piece as the sole child
  square.appendChild(piece);
}

function checkSpecialMoves(from, cm, to, p) {
  let tmp = { from, to };
  if (!cm) return tmp;
  const f = cm.flags,
    w = Math.round(squares[0].getBoundingClientRect().width);
  if (f.includes("p")) {
    tmp = { from, to, promotion: "q" };
    p.src = `https://images.chesscomfiles.com/chess-themes/pieces/neo/${w}/${cm.color}q.png`;
  }
  if (f.includes("e")) {
    const cid = cm.to[0] + cm.from[1];
    document
      .getElementById(cid)
      ?.removeChild(document.getElementById(cid).firstChild);
  }
  if (f.includes("k")) cm.color === "w" ? moveBot("h1f1") : moveBot("h8f8");
  if (f.includes("q")) cm.color === "w" ? moveBot("a1d1") : moveBot("a8d8");
  return tmp;
}

function removeHighlights() {
  squares.forEach((sq) => sq.classList.remove("validWhite", "validBlack"));
}

function resetPosition(p) {
  p.style.top = "";
  p.style.left = "";
}

function revertPosition(iv, closest, cs, p) {
  let did = cs.id;
  if (iv) {
    checkCapture(closest, p);
    did = closest.id;
  } else {
    cs.append(p);
  }
  return did;
}

function checkEndGame() {
  const t = chess.turn() === "b" ? "WHITE wins by" : "BLACK wins by";
  if (chess.in_checkmate()) {
    document.getElementById("winner").innerText = t;
    document.getElementById("endGameType").innerText = "CHECKMATE";
  } else if (chess.in_threefold_repetition()) {
    document.getElementById("endGameType").innerText = "DRAW";
    document.getElementById("endBy").innerText = "Threefold Repetition";
  } else if (chess.in_stalemate()) {
    document.getElementById("endGameType").innerText = "DRAW";
    document.getElementById("endBy").innerText = "Stalemate";
  } else if (chess.insufficient_material()) {
    document.getElementById("endGameType").innerText = "DRAW";
    document.getElementById("endBy").innerText = "Insufficient Material";
  } else if (chess.in_draw()) {
    document.getElementById("endGameType").innerText = "DRAW";
  }
  if (chess.game_over()) {
    document.getElementById("thinking").classList.remove("lds-grid");
  }
}

// --- Engine Move Fetch Logic ---
function sendFen() {
  fetch("/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value: chess.fen() }),
  })
    .then((response) => {
      if (!response.ok) throw new Error("Invalid engine response");
      return response.text();
    })
    .then((move) => {
      if (!move.match(/^[a-h][1-8][a-h][1-8][qrbn]?$/)) {
        throw new Error("moveBot failed: bad move format: " + move);
      }
      moveBot(move);
    })
    .catch((err) => {
      console.error(err.message);
      document.getElementById("thinking")?.classList.remove("lds-grid");
    });
}

// Call sendFen when needed based on player's color vs turn:
if (chess.turn() !== playerColor[0]) {
  sendFen();
  document.getElementById("thinking").classList.add("lds-grid");
}

function dropPiece(p, cs, vm) {
  const poss = potentialDrops(p);
  let did = cs.id;
  let chosen = null;

  if (poss.length) {
    const c = maxOverlap(p, poss);
    const valid = vm.some((m) => m.to === c.id);
    chosen = vm.find((m) => m.to === c.id);
    did = revertPosition(valid, c, cs, p);
  } else {
    cs.append(p);
  }

  resetPosition(p);
  removeHighlights();
  const tm = checkSpecialMoves(cs.id, chosen, did, p);
  chess.move(tm);

  // Check who should move next
  const currentTurn = chess.turn() === "w" ? "white" : "black";

  // If AI is the next to move
  if (currentTurn !== playerColor) {
    sendFen(); // triggers POST to /play and expects a move
    document.getElementById("thinking").classList.add("lds-grid");
  }

  checkEndGame();
}

document.getElementById("btn-restart").addEventListener("click", function () {
  fetch("/play/restart/", { method: "POST" }).then(() => location.reload());
});

document.getElementById("btn-switch").addEventListener("click", function () {
  fetch("/play/switch/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // Optional: include CSRF token if using it
      // "X-CSRFToken": getCSRFToken()
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to switch sides");
      }
      return response.json();
    })
    .then((data) => {
      const board = document.querySelector(".board");

      if (data.color === "black") {
        board.classList.add("flipped");
      } else {
        board.classList.remove("flipped");
      }

      location.reload(); // reload to re-render with new FEN + perspective
    })
    .catch((error) => {
      console.error("Switch sides failed:", error);
      alert("Error switching sides. Try again.");
    });
});

document.getElementById("btn-score").addEventListener("click", function () {
  fetch("/play/score/")
    .then((res) => res.json())
    .then((data) => alert(data.score));
});

document.getElementById("btn-autoplay").addEventListener("click", () => {
  const fen = chess.fen();
  fetch("/auto-play/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ fen: fen }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.move) {
        moveBot(data.move);
      }
    });
});

document.getElementById("btn-undo").addEventListener("click", () => {
  fetch("/undo/", { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      if (data.fen) {
        // Apply the FEN to the board manually if your logic allows
        location.reload(); // Simplest fallback
      } else {
        alert("Undo failed.");
      }
    })
    .catch((err) => {
      console.error("Undo error:", err.message);
      alert("Undo failed due to an error.");
    });
});

window.addEventListener("load", () => {
  const board = document.querySelector(".board");
  if (playerColor === "black") {
    board.classList.add("flipped");
  } else {
    board.classList.remove("flipped");
  }
});
