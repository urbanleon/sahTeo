#!/usr/bin/env python3
import time
import math

from chess import Move
import teo_chess
import teo_chess.polyglot
from typing import Optional, Tuple, List, Dict, NamedTuple
from collections import defaultdict

# ——————————————————————————————————————————————————————————
#                     CONFIGURARE ȘI DATE STATICE
# ——————————————————————————————————————————————————————————

PIECE_VALUES: Dict[int,int] = {
    teo_chess.PAWN:   100,
    teo_chess.KNIGHT: 320,
    teo_chess.BISHOP: 330,
    teo_chess.ROOK:   500,
    teo_chess.QUEEN:  900,
    teo_chess.KING:   20000,
}

# Midgame and endgame piece‐square tables for king interpolation
KING_MG = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]
KING_EG = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

# Single PST for midgame (other pieces)
PAWN_TABLE   = [0,0,0,0,0,0,0,0,
                5,10,10,-20,-20,10,10,5,
                5,-5,-10,0,0,-10,-5,5,
                0,0,0,20,20,0,0,0,
                5,5,10,25,25,10,5,5,
                10,10,20,30,30,20,10,10,
                50,50,50,50,50,50,50,50,
                0,0,0,0,0,0,0,0]
KNIGHT_TABLE = [-50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50]
BISHOP_TABLE = [-20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-10,-10,-10,-10,-10,-20]
ROOK_TABLE   = [ 0,0,0,5,5,0,0,0,
                -5,0,0,0,0,0,0,-5,
                -5,0,0,0,0,0,0,-5,
                -5,0,0,0,0,0,0,-5,
                -5,0,0,0,0,0,0,-5,
                -5,0,0,0,0,0,0,-5,
                 5,10,10,10,10,10,10, 5,
                 0,0,0,5,5,0,0,0]
QUEEN_TABLE  = [-20,-10,-10,-5,-5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5,  5,  5,  5,  0,-10,
                 -5,  0,  5,  5,  5,  5,  0, -5,
                  0,  0,  5,  5,  5,  5,  0, -5,
                -10,  5,  5,  5,  5,  5,  0,-10,
                -10,  0,  5,  0,  0,  0,  0,-10,
                -20,-10,-10,-5,-5,-10,-10,-20]

TABLES: Dict[int,List[int]] = {
    teo_chess.PAWN:   PAWN_TABLE,
    teo_chess.KNIGHT: KNIGHT_TABLE,
    teo_chess.BISHOP: BISHOP_TABLE,
    teo_chess.ROOK:   ROOK_TABLE,
    teo_chess.QUEEN:  QUEEN_TABLE,
}

# ——————————————————————————————————————————————————————————
#                       TRANSPOSITION TABLE
# ——————————————————————————————————————————————————————————

class TTEntry(NamedTuple):
    key:    int
    depth:  int
    score:  float
    flag:   int               # 0=exact,1=lower,2=upper
    move:   Optional[teo_chess.Move]

_TT_SIZE = 1 << 18
_TT: List[Optional[TTEntry]] = [None] * _TT_SIZE

def _get_key(board: teo_chess.Board) -> int:
    try:
        raw = board.transposition_key()
    except AttributeError:
        raw = board._transposition_key()
    if isinstance(raw, tuple):
        raw = raw[0] ^ raw[1]
    return raw

def _tt_probe(board: teo_chess.Board, depth: int, alpha: float, beta: float) -> Optional[float]:
    k = _get_key(board)
    e = _TT[k & (_TT_SIZE-1)]
    if e and e.key == k and e.depth >= depth:
        if e.flag == 0:
            return e.score
        if e.flag == 1 and e.score <= alpha:
            return e.score
        if e.flag == 2 and e.score >= beta:
            return e.score
    return None

def _tt_store(board: teo_chess.Board, depth: int, score: float, flag: int, move: Optional[teo_chess.Move]) -> None:
    k   = _get_key(board)
    idx = k & (_TT_SIZE-1)
    _TT[idx] = TTEntry(k, depth, score, flag, move)

# ——————————————————————————————————————————————————————————
#                       KILLER & HISTORY HEURISTICS
# ——————————————————————————————————————————————————————————

_KILLERS: Dict[int,List[Optional[Move]]] = defaultdict(lambda: [None, None, None, None])
_HISTORY: Dict[teo_chess.Move,int]            = defaultdict(int)
_COUNTER: Dict[int, Optional[teo_chess.Move]] = defaultdict(lambda: None)

# Pruning and search parameters
NULL_R            = 2
MAX_Q_DEPTH       = 4
FUTILITY_MARGIN   = 100
CHECK_EXTENSION   = 1

# Razoring margins per depth
RAZOR_MARGIN     = {1:200, 2:200, 3:150}

# Multi-cut parameters
MULTI_CUT_DEPTH  = 6
MULTI_CUT_REDUCE = 3
MULTI_CUT_COUNT  = 2
MULTI_CUT_TRY    = 3

# Tactical bonuses
PASSER_BONUS      = 30
OPEN_FILE_BONUS   = 20
OUTPOST_BONUS     = 40

# ——————————————————————————————————————————————————————————
#                         TIME MANAGEMENT
# ——————————————————————————————————————————————————————————

class TimeManager:
    def __init__(self, total_time: float, increment: float, moves_to_go: int):
        # total_time: timpul rămas în ceas înainte de mutare
        # increment: incrementul pe mutare
        # moves_to_go: mutările estimate până la control
        self.timebank    = total_time
        self.inc         = increment
        self.to_go       = moves_to_go
        self.last_stamp  = time.time()

    def allocate(self, board: teo_chess.Board) -> float:
        """Alocă timp pentru următoarea iterație de deepening."""
        now       = time.time()
        elapsed   = now - self.last_stamp
        # scade timpul consumat
        self.timebank = max(0.0, self.timebank - elapsed)
        self.last_stamp = now

        moves_left = max(1, self.to_go)
        mobility   = board.legal_moves.count()

        # bază simplă: fraction din rest
        base       = self.timebank / moves_left
        # factor în funcție de complexitate (≈număr mutări)
        factor     = min(2.0, 1.0 + (mobility - 20) / 40.0)
        # adaugă un pic din increment
        alloc      = base * factor + self.inc

        # nu lua mai mult de 70% din ce-a mai rămas
        return min(alloc, self.timebank * 0.7)


# ——————————————————————————————————————————————————————————
#                         STATIC EXCHANGE EVAL
# ——————————————————————————————————————————————————————————

def see(board: teo_chess.Board, mv: teo_chess.Move) -> int:
    victim   = board.piece_type_at(mv.to_square) or mv.promotion or teo_chess.PAWN
    attacker = board.piece_type_at(mv.from_square) or teo_chess.PAWN
    gains = [PIECE_VALUES[victim] - PIECE_VALUES[attacker]]
    board.push(mv)
    side, depth = board.turn, 1
    while True:
        attackers = board.attackers(side, mv.to_square)
        if not attackers:
            break
        sq = min(attackers, key=lambda s: PIECE_VALUES[board.piece_type_at(s) or teo_chess.PAWN])
        cap = board.piece_type_at(sq) or teo_chess.PAWN
        gains.append(PIECE_VALUES[cap] - gains[-1])
        board.push(teo_chess.Move(sq, mv.to_square))
        side = not side
        depth += 1
    for _ in range(depth):
        board.pop()
    for i in range(len(gains)-2, -1, -1):
        gains[i] = max(-gains[i+1], gains[i])
    return gains[0]

# ——————————————————————————————————————————————————————————
#                        MOVE ORDERING
# ——————————————————————————————————————————————————————————

def score_move(board: teo_chess.Board, mv: teo_chess.Move, ply: int) -> int:
    # 1) PV-move din TT
    entry = _TT[_get_key(board) & (_TT_SIZE - 1)]
    if entry and entry.move == mv:
        return 10_000_000

    # 2) Counter-move heuristic
    cnt = _COUNTER.get(ply)
    if cnt is not None and mv == cnt:
        return 9_750_000

    # 3) Killer-moves
    killers = _KILLERS[ply]
    if mv == killers[0]:
        return 9_000_000
    if mv in killers[1:4]:
        return 8_000_000

    # 4) Capturi (SEE + history)
    if board.is_capture(mv):
        return see(board, mv) * 100 + _HISTORY[mv]

    # 5) Rest: history heuristic
    return _HISTORY[mv]



def ordered_moves(board: teo_chess.Board, ply: int) -> List[teo_chess.Move]:
    mvs = list(board.legal_moves)
    mvs.sort(key=lambda mv: score_move(board,mv,ply), reverse=True)
    return mvs

# ——————————————————————————————————————————————————————————
#                       EVALUATION FUNCTIONS
# ——————————————————————————————————————————————————————————

def game_phase(board: teo_chess.Board) -> float:
    total = sum(PIECE_VALUES[p] * len(board.pieces(p,c))
                for p in PIECE_VALUES for c in (teo_chess.WHITE,teo_chess.BLACK))
    return max(0.0, min(1.0, total / (2 * PIECE_VALUES[teo_chess.QUEEN] * 2)))

def evaluate_passers(board: teo_chess.Board) -> float:
    bonus = 0.0
    for color, sign in ((teo_chess.BLACK,1),(teo_chess.WHITE,-1)):
        step = 1 if color==teo_chess.BLACK else -1
        for sq in board.pieces(teo_chess.PAWN, color):
            f, r = sq%8, sq//8
            front = range(r+step, 8 if color==teo_chess.BLACK else -1, step)
            if all(board.piece_type_at(rr*8+f)!=teo_chess.PAWN for rr in front if 0<=rr<8):
                bonus += sign * PASSER_BONUS
    return bonus

def evaluate_open_files(board: teo_chess.Board) -> float:
    score = 0.0
    for color, sign in ((teo_chess.BLACK,1),(teo_chess.WHITE,-1)):
        for file in range(8):
            if all(board.piece_type_at(r*8+file)!=teo_chess.PAWN for r in range(8)):
                for sq in board.pieces(teo_chess.ROOK, color):
                    if sq%8==file:
                        score += sign * OPEN_FILE_BONUS
    return score

def evaluate_outposts(board: teo_chess.Board) -> float:
    bonus = 0.0
    for color, sign in ((teo_chess.BLACK,1),(teo_chess.WHITE,-1)):
        enemy = not color
        step = 1 if color==teo_chess.BLACK else -1
        for ptype in (teo_chess.KNIGHT, teo_chess.BISHOP):
            for sq in board.pieces(ptype, color):
                f, r = sq%8, sq//8
                br, fr = r-step, r+step
                sup = False
                if 0<=br<8:
                    pc = board.piece_at(br*8+f)
                    if pc and pc.piece_type==teo_chess.PAWN and pc.color==color:
                        sup = True
                att = False
                if 0<=fr<8:
                    pc2 = board.piece_at(fr*8+f)
                    if pc2 and pc2.piece_type==teo_chess.PAWN and pc2.color==enemy:
                        att = True
                if sup and not att:
                    bonus += sign * OUTPOST_BONUS
    return bonus

def evaluate_king_safety(board: teo_chess.Board) -> float:
    score = 0.0
    for color, sign in ((teo_chess.WHITE,1),(teo_chess.BLACK,-1)):
        ksq = board.king(color); kf, kr = ksq%8, ksq//8
        for df in (-1,0,1):
            file = kf+df
            if 0<=file<8:
                for dr in (1,2,3):
                    r = kr + (dr if color==teo_chess.WHITE else -dr)
                    if 0<=r<8 and board.piece_type_at(r*8+file)!=teo_chess.PAWN:
                        score -= sign * 10
        if all(board.piece_type_at(r*8+7)!=teo_chess.PAWN for r in range(8)) and abs(kf-7)<=1:
            score -= sign * 20
    return score

def evaluate_pawn_storm(board: teo_chess.Board) -> float:
    score = 0.0
    for color, sign in ((teo_chess.WHITE,1),(teo_chess.BLACK,-1)):
        ek = board.king(not color); ekf, ekr = ek%8, ek//8
        for sq in board.pieces(teo_chess.PAWN, color):
            f, r = sq%8, sq//8
            if abs(f-ekf)<=1:
                adv = (r-ekr) if color==teo_chess.WHITE else (ekr-r)
                if adv>0:
                    support = sum(
                        1 for df,dr in [(-1,0),(1,0),(0,1),(0,-1)]
                        if 0<=r+dr<8 and 0<=f+df<8 and
                           board.piece_type_at((r+dr)*8+f+df) in (teo_chess.PAWN,teo_chess.KNIGHT,teo_chess.BISHOP)
                    )
                    score += sign * (5*adv + 3*support)
    return score

def evaluate_outposts_advanced(board: teo_chess.Board) -> float:
    score = 0.0
    for color, sign in ((teo_chess.WHITE,1),(teo_chess.BLACK,-1)):
        ksq = board.king(color)
        for ptype in (teo_chess.KNIGHT, teo_chess.BISHOP):
            for sq in board.pieces(ptype, color):
                if not any(
                    board.piece_type_at(a)==teo_chess.PAWN and board.piece_at(a).color!=color
                    for a in board.attacks(sq)
                ):
                    atk = len(board.attackers(color, sq))
                    dist = abs((sq//8)-(ksq//8)) + abs((sq%8)-(ksq%8))
                    score += sign * (atk*10 - max(0,dist-2)*2)
    return score

def evaluate_mobility_refined(board: teo_chess.Board) -> float:
    mob = list(board.legal_moves)
    base = len(mob); bonus = 0
    for mv in mob:
        f,r = mv.to_square%8, mv.to_square//8
        if 2<=f<=5 and 2<=r<=5: bonus += 2
        if all(board.piece_type_at(rr*8+f)!=teo_chess.PAWN for rr in range(8)): bonus += 1
        if f in (0,7): bonus += 1
    return 0.1*base + 0.05*bonus

def evaluate_rook_on_seventh(board: teo_chess.Board) -> float:
    score = 0.0
    for color, sign, tr in ((teo_chess.WHITE,1,6),(teo_chess.BLACK,-1,1)):
        for sq in board.pieces(teo_chess.ROOK, color):
            if sq//8 == tr:
                f = sq%8
                if not any(
                    board.piece_type_at((tr + (1 if color==teo_chess.WHITE else -1))*8+f)==teo_chess.PAWN
                    and board.piece_at((tr + (1 if color==teo_chess.WHITE else -1))*8+f).color!=color
                    for _ in (0,)
                ):
                    score += sign * 30
    return score

def evaluate_bishop_vs_knight(board: teo_chess.Board) -> float:
    score = 0.0
    for color, sign in ((teo_chess.WHITE,1),(teo_chess.BLACK,-1)):
        bcount = len(board.pieces(teo_chess.BISHOP, color))
        if bcount>=2:
            of = sum(1 for f in range(8)
                     if all(board.piece_type_at(r*8+f)!=teo_chess.PAWN for r in range(8)))
            score += sign * min(20,5*of)
        for sq in board.pieces(teo_chess.KNIGHT, color):
            f,r = sq%8, sq//8
            if not any(
                board.piece_type_at(rr*8+f)==teo_chess.PAWN
                and ((rr>r) if color==teo_chess.WHITE else (rr<r))
                for rr in range(8)
            ):
                score -= sign * 10
    return score

def evaluate_material_imbalance(board: teo_chess.Board) -> float:
    score = 0.0
    for color, sign in ((teo_chess.WHITE,1),(teo_chess.BLACK,-1)):
        kn = len(board.pieces(teo_chess.KNIGHT, color))
        bi = len(board.pieces(teo_chess.BISHOP,  color))
        pw = len(board.pieces(teo_chess.PAWN,    color))
        if kn>=2 and bi==1 and pw>=1:
            score += sign * 15
    return score

def evaluate(board: teo_chess.Board) -> float:
    if board.is_checkmate():
        return -99999.0 if board.turn else 99999.0
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

    mg = game_phase(board)
    eg = 1.0 - mg
    sc = 0.0

    # material + PST
    for p,tbl in TABLES.items():
        base = PIECE_VALUES[p]
        for sq in board.pieces(p, teo_chess.BLACK):
            sc += base + tbl[sq]
        for sq in board.pieces(p, teo_chess.WHITE):
            sc -= base + tbl[teo_chess.square_mirror(sq)]

    # king PST interpolation
    for sq in board.pieces(teo_chess.KING, teo_chess.BLACK):
        sc += mg * KING_MG[sq] + eg * KING_EG[sq]
    for sq in board.pieces(teo_chess.KING, teo_chess.WHITE):
        msq = teo_chess.square_mirror(sq)
        sc -= mg * KING_MG[msq] + eg * KING_EG[msq]

    # bishop pair
    if len(board.pieces(teo_chess.BISHOP, teo_chess.BLACK)) >= 2:
        sc += 50
    if len(board.pieces(teo_chess.BISHOP, teo_chess.WHITE)) >= 2:
        sc -= 50

    # pawn structure
    for color, sign in ((teo_chess.BLACK,1),(teo_chess.WHITE,-1)):
        files = [sq%8 for sq in board.pieces(teo_chess.PAWN, color)]
        for f in set(files):
            cnt = files.count(f)
            if cnt>1:
                sc += sign * -20 * (cnt-1)
            if all(nb not in files for nb in (f-1,f+1)):
                sc += sign * -20

    # center control
    for c in (teo_chess.D4, teo_chess.E4, teo_chess.D5, teo_chess.E5):
        pc = board.piece_at(c)
        if pc:
            sc += 25 if pc.color==teo_chess.BLACK else -25

    # tactical & positional bonuses
    sc += evaluate_passers(board)
    sc += evaluate_open_files(board)
    sc += evaluate_outposts(board)
    sc += evaluate_king_safety(board)
    sc += evaluate_pawn_storm(board)
    sc += evaluate_outposts_advanced(board)
    sc += evaluate_mobility_refined(board)
    sc += evaluate_rook_on_seventh(board)
    sc += evaluate_bishop_vs_knight(board)
    sc += evaluate_material_imbalance(board)

    # mobility
    mob = board.legal_moves.count()
    sc += 0.1 * mob * (1 if board.turn==teo_chess.BLACK else -1)

    # king safety (attacks around king)
    for color, sign in ((teo_chess.BLACK,1),(teo_chess.WHITE,-1)):
        ksq = board.king(color)
        att = sum(1 for a in board.attacks(ksq) if board.is_attacked_by(not color,a))
        sc += sign * -10 * min(att,4)

    return sc

# ——————————————————————————————————————————————————————————
#                          QUIESCENCE SEARCH
# ——————————————————————————————————————————————————————————

def quiesce(board: teo_chess.Board, alpha: float, beta: float, depth: int=0) -> float:
    stand = evaluate(board)
    if stand + FUTILITY_MARGIN*(MAX_Q_DEPTH-depth) < alpha or depth>=MAX_Q_DEPTH:
        return stand
    if stand>alpha:
        alpha = stand

    for mv in ordered_moves(board, depth):
        if not board.is_capture(mv):
            continue
        if see(board,mv) + 10 < alpha:
            continue
        board.push(mv)
        val = -quiesce(board, -beta, -alpha, depth+1)
        board.pop()
        if val>=beta:
            return beta
        if val>alpha:
            alpha = val
    return alpha

# ——————————————————————————————————————————————————————————
#                      NEGASCOUT (PVS) + NULL‐MOVE + LMR + EXT
# ——————————————————————————————————————————————————————————

def negascout(board: teo_chess.Board,
              depth: int,
              alpha: float,
              beta: float,
              ply: int = 0
) -> Tuple[Optional[teo_chess.Move], float]:
    """
    Principal Variation Search (PVS) cu:
      - razoring
      - multi-cut
      - transposition table probe
      - null-move pruning
      - hard late-move pruning
      - late-move reductions (LMR)
      - aspiration re-search (în find_best_move)
      - killer moves, counter moves, history heuristic
    """

    # ── 1) Razoring ──
    if depth in RAZOR_MARGIN:
        static = evaluate(board)
        if static + RAZOR_MARGIN[depth] < alpha:
            return None, static

    # ── 2) Multi-cut ──
    if depth >= MULTI_CUT_DEPTH and ply > 0:
        cnt = 0
        for mv in ordered_moves(board, ply)[:MULTI_CUT_TRY]:
            board.push(mv)
            _, sc = negascout(board, depth - MULTI_CUT_REDUCE, -beta, -beta + 1, ply + 1)
            board.pop()
            if -sc >= beta:
                cnt += 1
                if cnt >= MULTI_CUT_COUNT:
                    return None, beta

    # ── 3) Transposition Table probe ──
    prov = _tt_probe(board, depth, alpha, beta)
    if prov is not None:
        return None, prov

    # ── 4) Leaf node? ──
    if depth <= 0:
        return None, quiesce(board, alpha, beta)

    # ── 5) Null-move pruning ──
    R = min(NULL_R + 1, max(1, depth // 4))
    if depth > R + 1 and not board.is_check():
        board.push(teo_chess.Move.null())
        _, nm = negascout(board, depth - R - 1, -beta, -beta + 1, ply + 1)
        board.pop()
        if -nm >= beta:
            return None, beta

    best_mv, first = None, True
    b = beta

    # ── 6) Main move loop ──
    for i, mv in enumerate(ordered_moves(board, ply)):
        # 6.a) Hard late-move pruning
        if (i >= 4
            and depth >= 3
            and not board.is_capture(mv)
            and not board.gives_check(mv)):
            continue

        board.push(mv)
        ext = CHECK_EXTENSION if board.is_check() else 0

        # 6.b) Late-move reduction
        if i > 0 and depth >= 3 and not board.is_capture(mv) and not board.is_check():
            reduced_depth = depth - 2 + ext
            _, sc = negascout(board, reduced_depth, -b, -alpha, ply + 1)
        else:
            _, sc = negascout(board, depth - 1 + ext, -b, -alpha, ply + 1)

        board.pop()
        sc = -sc

        # 6.c) Principal Variation re-search
        if not first and alpha < sc < beta:
            board.push(mv)
            _, sc = negascout(board, depth - 1 + ext, -beta, -alpha, ply + 1)
            board.pop()
            sc = -sc

        # 6.d) Update alpha & best move
        if sc > alpha:
            alpha, best_mv = sc, mv

        # 6.e) Beta cutoff
        if alpha >= beta:
            # store lower-bound in TT
            _tt_store(board, depth, beta, flag=1, move=mv)

            # counter-move heuristic
            _COUNTER[ply] = mv

            # killer moves (păstrează max 4)
            killers = _KILLERS[ply]
            if mv in killers:
                killers.remove(mv)
            killers.insert(0, mv)
            _KILLERS[ply] = killers[:4]

            # history heuristic boost
            _HISTORY[mv] += (depth * depth) * 2

            return best_mv, beta

        first = False
        b = alpha + 1

    # ── 7) No cutoff: exact score ──
    if best_mv:
        _HISTORY[best_mv] += depth * depth
    _tt_store(board, depth, alpha, flag=0, move=best_mv)
    return best_mv, alpha


# ——————————————————————————————————————————————————————————
#               ITERATIVE DEEPENING + TIME MANAGEMENT
# ——————————————————————————————————————————————————————————

def search_best_move(board: teo_chess.Board,
                     time_left:  float,
                     increment:  float,
                     moves_to_go:int,
                     max_depth:  int   = 6
) -> Tuple[Optional[teo_chess.Move], float]:
    """Iterative deepening cu time management adaptiv."""
    tm = TimeManager(time_left, increment, moves_to_go)
    best_mv, best_sc = None, 0.0

    for depth in range(1, max_depth+1):
        # alocă buget de timp pentru această adâncime
        alloc = tm.allocate(board)
        deadline = time.time() + alloc

        # ferestră de aspirație
        window = max(50, abs(best_sc)*0.1)
        alpha, beta = best_sc - window, best_sc + window

        # prima căutare în ferestră
        mv, sc = negascout(board, depth, alpha, beta, ply=0)
        # dacă scapă din ferestră, căutăm full
        if sc <= alpha or sc >= beta:
            mv, sc = negascout(board, depth, -math.inf, math.inf, ply=0)

        if mv is not None:
            best_mv, best_sc = mv, sc

        # dacă am atins sau depășit bugetul de timp, ne oprim
        if time.time() >= deadline:
            break

    return best_mv, best_sc



# ——————————————————————————————————————————————————————————
#                    OPENING‐BOOK FALLBACK
# ——————————————————————————————————————————————————————————

def opening_move(board: teo_chess.Board) -> Tuple[Optional[teo_chess.Move], float]:
    try:
        with teo_chess.polyglot.open_reader("pwned.polyglot.bin") as reader:
            return reader.weighted_choice(board).move, 0.0
    except:
        # pentru test: 5s total, 0.2s increment, ~40 mutări până la control
        return search_best_move(board,
                                time_left=5.0,
                                increment=0.2,
                                moves_to_go=40,
                                max_depth=4)


# ——————————————————————————————————————————————————————————
#                         CLI MAIN PENTRU TESTARE
# ——————————————————————————————————————————————————————————

def main() -> None:
    board = teo_chess.Board()
    print(board.unicode(borders=True), "\n")
    while not board.is_game_over():
        if board.turn == teo_chess.WHITE:
            san = input("WHITE's move: ")
            try:
                board.push_san(san)
            except ValueError:
                print("Invalid SAN, try again.")
                continue
        else:
            mv, sc = opening_move(board)
            if mv is None:
                print("No moves left!")
                break
            print(f"BLACK plays {board.san(mv)}  |  Eval = {sc:.1f}")
            board.push(mv)
        print(board.unicode(borders=True), "\n")
    print("Game over:", board.result())

def reset_search() -> None:
    global _TT, _KILLERS, _HISTORY
    _TT = [None] * _TT_SIZE
    _KILLERS.clear()
    _HISTORY.clear()

if __name__=="__main__":
    main()
