#!/usr/bin/env python3
import re
import teo_chess

def visualize_san_line(san_line: str):
    """
    Primește un șir de mutări în SAN (de exemplu "1. d4 d5 2. Nf3 g5 ... 1-0"),
    aplică mutările pe board și afișează poziția finală ca în engine.py.
    """
    board = teo_chess.Board()
    # extrage doar token-urile cu mutări (ignoră numerotările și rezultatul)
    tokens = re.findall(r"[KQRNB]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRNB])?|O-O-O|O-O", san_line)
    for san in tokens:
        board.push_san(san)
    # afișare identică cu engine.py
    print(board.unicode(borders=True))
    # coordonate de jos
    print("  a   b   c   d   e   f   g   h\n")

if __name__ == "__main__":
    examples = [
        # Partida 1
        "1. d4 d5 2. Nf3 g5 3. Bxg5 Nc6 4. c4 dxc4 5. e4 Nf6 6. Bxc4 Ng8 7. Qb3 Nf6 8. Bxf7+ Kd7 9. Qe6# 1-0",
        # Partida 13
        "1. Nf3 Nf6 2. c4 h5 3. e3 Rh6 4. d4 Rh8 5. Bd3 b6 6. e4 g5 7. e5 g4 8. Nc3 d5 9. Ng5 Bh6 10. O-O dxc4 11. Qa4+ Nc6 12. Qxc6+ Bd7 13. Qxc4 Bc6 14. Qxf7+ Kd7 15. Bf5# 1-0",
        # Partida 31
        "1. d4 d5 2. c4 c6 3. Nf3 g5 4. cxd5 Kd7 5. dxc6+ Nxc6 6. d5 Qa5+ 7. Nc3 Nb4 8. e4 g4 9. Ne5+ Kd8 10. Bb5 Nc2+ 11. Qxc2 f6 12. Nf7+ Kc7 13. Bd2 Bd7 14. Na4+ Kb8 15. Bxd7 a6 16. Bxa5 e6 17. Qc7+ Ka7 18. Rc1 exd5 19. Bb6# 1-0",
        # Partida 50
        "1. e4 e5 2. g4 h5 3. Na3 Nc6 4. Nb1 hxg4 5. Na3 Bxa3 6. Qxg4 Bf8 7. Qxg7 Bxg7 8. a3 d5 9. h3 dxe4 10. d3 Be6 11. d4 Nxd4 12. Bb5+ Nxb5 13. b3 Nd4 14. Bd2 Nxc2+ 15. Kd1 Qd3 16. Rh2 Bxb3 17. Nf3 Nd4+ 18. Kc1 Qc2# 0-1",
    ]

    for i, san in enumerate(examples, 1):
        print(f"\n=== Poziția finală a partidei {i} ===\n")
        visualize_san_line(san)
