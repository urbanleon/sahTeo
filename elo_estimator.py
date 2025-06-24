#!/usr/bin/env python3
import sys
import time
import random
import math
import chess
import chess.engine
import chess.pgn
from statistics import mean, pstdev
from engine import search_best_move  # Your full-strength TEO engine
from typing import Tuple

# ————————————————— CONFIGURAȚIUNI —————————————————
STOCKFISH_PATH   = r"C:\Code\Licenta\stockfish\stockfish-windows-x86-64-avx2.exe"
STOCKFISH_ELO    = 2900
SF_TIME          = 0.5     # secunde per mutare Stockfish
MY_TIME          = 1.0    # secunde per mutare MyEngine
MY_INCREMENT     = 0.05    # increment per mutare MyEngine
MY_MOVES_TO_GO   = 40      # mutări estimate până la următorul control
NUM_GAMES        = 50      # creștem numărul de partide
MAX_MOVES        = 200
PGN_FILE         = "games.pgn"

# mini-carte de deschideri (SAN)
OPENINGS = [
    "e4 e5", "d4 d5", "c4 c5", "Nf3 Nf6", "g3 d5",
    "e4 c5", "d4 Nf6", "c4 e6", "Nf3 d5", "g3 Nf6"
]

def simulate_game(idx: int, sf: chess.engine.SimpleEngine, white_is_my: bool
) -> Tuple[chess.pgn.Game, float]:
    board = chess.Board()
    # Aplicăm o deschidere pre-încărcată
    line = OPENINGS[idx % len(OPENINGS)].split()
    for san in line:
        board.push_san(san)

    game = chess.pgn.Game()
    game.headers["Event"] = f"MyEngine vs Stockfish ({idx})"
    game.headers["White"] = "MyEngine" if white_is_my else "Stockfish"
    game.headers["Black"] = "Stockfish" if white_is_my else "MyEngine"
    node = game.add_line(board.move_stack)

    ply = len(board.move_stack)
    while not board.is_game_over() and ply < MAX_MOVES:
        if (board.turn == chess.WHITE) == white_is_my:
            mv, _ = search_best_move(
                board,
                time_left   = MY_TIME,
                increment   = MY_INCREMENT,
                moves_to_go = MY_MOVES_TO_GO,
                max_depth   = 6
            )
        else:
            try:
                res = sf.play(board, chess.engine.Limit(time=SF_TIME))
                mv  = res.move
            except Exception:
                mv = None

        if mv is None:
            break

        board.push(mv)
        node = node.add_variation(mv)
        ply += 1

    result = board.result(claim_draw=True)
    game.headers["Result"] = result
    score_map = {"1-0":1.0, "0-1":0.0, "1/2-1/2":0.5}
    return game, score_map.get(result, 0.5)

def main():
    print(f"\nEstimare ELO MyEngine vs Stockfish ({NUM_GAMES} jocuri)\n")

    try:
        sf = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except FileNotFoundError:
        print("🔥 Stockfish nu a fost găsit la:", STOCKFISH_PATH, file=sys.stderr)
        sys.exit(1)

    sf.configure({"UCI_LimitStrength": True, "UCI_Elo": STOCKFISH_ELO})
    print(f"✅ Stockfish setat la Elo = {STOCKFISH_ELO}\n")

    # pregătim alternarea culorilor aleator
    colors = [True]*(NUM_GAMES//2) + [False]*(NUM_GAMES//2)
    if len(colors) < NUM_GAMES:
        colors.append(True)
    random.shuffle(colors)

    games, scores = [], []
    for i, white_is_my in enumerate(colors, start=1):
        print(f"▶ Partida {i}/{NUM_GAMES}… ", end="", flush=True)
        game, score = simulate_game(i, sf, white_is_my)
        games.append(game)
        scores.append(score)
        if score == 1.0:
            print("MyEngine câștigă")
        elif score == 0.0:
            print("Stockfish câștigă")
        else:
            print("remiză")

    sf.quit()

    # ————————————————— Calcul ELO cu interval de încredere —————————————————
    avg = mean(scores)
    std = pstdev(scores) if NUM_GAMES > 1 else 0.0
    se  = std / math.sqrt(NUM_GAMES)
    if 0 < avg < 1:
        diff    = -400 * math.log10(1/avg - 1)
        elo     = STOCKFISH_ELO + diff
        # limite 95% CI
        lo_s = max(1e-6, avg - 1.96*se)
        hi_s = min(1-1e-6, avg + 1.96*se)
        diff_lo = -400 * math.log10(1/lo_s - 1)
        diff_hi = -400 * math.log10(1/hi_s - 1)
        elo_lo  = STOCKFISH_ELO + diff_lo
        elo_hi  = STOCKFISH_ELO + diff_hi
    else:
        elo    = STOCKFISH_ELO + (400 if avg >= 1 else -400)
        elo_lo = elo_hi = None

    # Raport final
    print(f"\n✅ Rezultate: {scores}")
    print(f"▶ Scor mediu: {avg:.3f}  (σ={std:.3f})")
    if elo_lo is not None:
        print(f"▶ ELO estimat MyEngine: {round(elo)}  (95% CI: {round(elo_lo)}–{round(elo_hi)})\n")
    else:
        print(f"▶ ELO estimat MyEngine: {round(elo)}\n")

    # Salvăm PGN-urile
    with open(PGN_FILE, "w", encoding="utf-8") as f:
        for g in games:
            f.write(str(g))
            f.write("\n\n")
    print(f"🌟 PGN-ul jocurilor a fost salvat în “{PGN_FILE}” – deschide-l cu orice viewer PGN!\n")

if __name__ == "__main__":
    main()
