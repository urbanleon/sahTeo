#!/usr/bin/env python3
import chess
import chess.engine
import time

pawntable = [0,  0,  0,  0,  0,  0,  0,  0,
             5, 10, 10,-20,-20, 10, 10,  5,
             5, -5,-10,  0,  0,-10, -5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5,  5, 10, 25, 25, 10,  5,  5,
            10, 10, 20, 30, 30, 20, 10, 10,
            50, 50, 50, 50, 50, 50, 50, 50,
             0,  0,  0,  0,  0,  0,  0,  0]

knightstable = [-50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50]

bishoptable = [-20,-10,-10,-10,-10,-10,-10,-20,
               -10,  5,  0,  0,  0,  0,  5,-10,
               -10, 10, 10, 10, 10, 10, 10,-10,
               -10,  0, 10, 10, 10, 10,  0,-10,
               -10,  5,  5, 10, 10,  5,  5,-10,
               -10,  0,  5, 10, 10,  5,  0,-10,
               -10,  0,  0,  0,  0,  0,  0,-10,
               -20,-10,-10,-10,-10,-10,-10,-20]

rooktable = [0,  0,  0,  5,  5,  0,  0,  0,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
             5, 10, 10, 10, 10, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0]

queentable = [-20,-10,-10, -5, -5,-10,-10,-20,
              -10,  0,  0,  0,  0,  0,  0,-10,
              -10,  5,  5,  5,  5,  5,  0,-10,
                0,  0,  5,  5,  5,  5,  0, -5,
               -5,  0,  5,  5,  5,  5,  0, -5,
              -10,  0,  5,  5,  5,  5,  0,-10,
              -10,  0,  0,  0,  0,  0,  0,-10,
              -20,-10,-10, -5, -5,-10,-10,-20]

kingtable = [20, 30, 10,  0,  0, 10, 30, 20,
             20, 20,  0,  0,  0,  0, 20, 20,
            -10,-20,-20,-20,-20,-20,-20,-10,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30]

pawntable = [i / 10 for i in pawntable]
knightstable = [i / 10 for i in knightstable]
bishoptable = [i / 10 for i in bishoptable]
rooktable = [i / 10 for i in rooktable]
queentable = [i / 10 for i in queentable]
kingtable = [i / 10 for i in kingtable]


def evaluate(board):
    if board.is_checkmate():
        if not board.turn:
            return 9999
        else:
            return -9999
    if board.is_stalemate():
        return 0

    pawn = sum([pawntable[i] + 10 for i in board.pieces(chess.PAWN, chess.BLACK)])
    pawn += sum([-pawntable[chess.square_mirror(i)] + -10 for i in board.pieces(chess.PAWN, chess.WHITE)])

    knight = sum([knightstable[i] + 30 for i in board.pieces(chess.KNIGHT, chess.BLACK)])
    knight += sum([-knightstable[chess.square_mirror(i)] + -30 for i in board.pieces(chess.KNIGHT, chess.WHITE)])

    bishop = sum([bishoptable[i] + 30 for i in board.pieces(chess.BISHOP, chess.BLACK)])
    bishop += sum([-bishoptable[chess.square_mirror(i)] + -30 for i in board.pieces(chess.BISHOP, chess.WHITE)])


    rook = sum([rooktable[i] + 50 for i in board.pieces(chess.ROOK, chess.BLACK)])
    rook += sum([-rooktable[chess.square_mirror(i)] + -50 for i in board.pieces(chess.ROOK, chess.WHITE)])

    queen = sum([queentable[i] + 90 for i in board.pieces(chess.QUEEN, chess.BLACK)])
    queen += sum([-queentable[chess.square_mirror(i)] + -90 for i in board.pieces(chess.QUEEN, chess.WHITE)])

    king = sum([kingtable[i] + 900 for i in board.pieces(chess.KING, chess.BLACK)])
    king += sum([-kingtable[chess.square_mirror(i)] + -900 for i in board.pieces(chess.KING, chess.WHITE)])

    return pawn + knight + rook + queen + king

# def evaluate(board):
#
#     white = {"P":-10, "N":-30, "B":-30, "R":-50, "Q":-90, "K":-900}
#     black = {"p":10, "n":30, "b":30, "r":50, "q":90, "k":900}
#     fen = board.board_fen()
#
#     w_score = 0
#     b_score = 0
#
#     for k,v in white.items():
#         w_score += fen.count(k) * v
#     for k,v in black.items():
#         b_score += fen.count(k) * v
#     return w_score + b_score


def minimax(board, depth, turn, alpha, beta):
    if (depth == 0):
        return None, evaluate(board)

    possible_moves = list(board.legal_moves)

    #change to random choice
    possible_moves.reverse()


    if (turn == 1): #MAX
        max_score = -9999
        max_move = None
        # maybe change to random choice to
        # prevent repeated moves

        for move in possible_moves:
            temp_board = board.copy()
            temp_board.push(move)
            (_, score) = minimax(temp_board, depth - 1, not turn, alpha, beta)

            # if (depth == 4):
            #     print("mv: ", board.san(move), " score: ", score)

            if score > max_score:
                max_score = score
                max_move = move

            if max_score > alpha:
                alpha = max_score

            if alpha >= beta:
                break
        if max_score == -9999 and possible_moves:
            max_move = possible_moves[0]

        return max_move, max_score

    else: #MIN
        min_score = 9999
        min_move = None
        # min_move = possible_moves[0]

        for move in possible_moves:
            temp_board = board.copy()
            temp_board.push(move)
            (_, score) = minimax(temp_board, depth - 1, not turn, alpha, beta)

            # if (depth == 3):
            #     print("mv: ", board.san(move), " score: ", score)


            if score < min_score:
                min_score = score
                min_move = move

            if min_score < beta:
                beta = min_score

            if alpha >= beta:
                break

        return min_move, min_score


def print_captured(board):
    remaining = board.board_fen()
    white = {'P': 0, 'N': 0, 'B': 0, 'Q': 0, 'K': 0, 'R': 0}
    black = {'p': 0,'n': 0,'b': 0,'q': 0,'k': 0,'r': 0}

    for k, v in white.items():
        if k == 'P':
            white[k] = 8 - remaining.count(k)
        elif k in ['N','B','R']:
            white[k] = 2 - remaining.count(k)
        else:
            white[k] = 1 - remaining.count(k)

    for k, v in black.items():
        if k == 'p':
            black[k] = 8 - remaining.count(k)
        elif k in ['n','b','r']:
            black[k] = 2 - remaining.count(k)
        else:
            black[k] = 1 - remaining.count(k)

    print('\n')
    for k, v in white.items():
        print(chess.UNICODE_PIECE_SYMBOLS[k] * v, end=' ')
    print('\n')
    for k, v in black.items():
        print(chess.UNICODE_PIECE_SYMBOLS[k] * v, end=' ')
    print('\n')

def main():
    engine = chess.engine.SimpleEngine.popen_uci("C:/Code/Licenta/stockfish/stockfish-windows-x86-64-avx2.exe")
    engine.configure({"Skill Level": "0"})
    # engine.configure({"UCI_LimitStrength":"true", "UCI_Elo":"1350"})
    board = chess.Board()
    turn = 0
    print(board.unicode(borders=True))
    print("\n")

    while (not board.is_game_over()):
        if (turn % 2 == 0):
            if board.is_check():
                print("WHITE is in CHECK.")

            w_move = engine.play(board, chess.engine.Limit(time=0.1))
            print("Stockfish's move: ", board.san(w_move.move))
            print('\n')
            board.push(w_move.move)

        else:
            if board.is_check():
                print("BLACK is in CHECK.")

            b_move, score = minimax(board, 4, 1, -10000, 10000)
            print("BLACK's move: ", board.san(b_move))
            print('\n')
            board.push(b_move)

        print(board.unicode(borders=True))
        print_captured(board)
        # time.sleep(2)
        turn += 1

    if (board.is_checkmate()):
        print("Checkmate!")
    else:
        print("Game over!")

    end_game = board.result()

    if end_game == "1-0":
        print("WHITE wins!")
    elif end_game == "0-1":
        print("BLACK wins!")
    else:
        print("It's a DRAW!")

    engine.quit()

if __name__ == "__main__":
    main()
