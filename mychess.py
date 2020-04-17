#!/usr/bin/env python3
import chess
# import random

# def player(board):
#     move = random.choice(list(board.legal_moves))
#     return move.uci()

def evaluateRoot(board):
    #does not work
    # white = {"P":10, "N":30, "B":30, "R":50, "Q":90, "K":900}
    # black = {"p":-10, "n":-30, "b":-30, "r":-50, "q":-90, "k":-900}
    #works
    white = {"P":-10, "N":-30, "B":-30, "R":-50, "Q":-90, "K":-900}
    black = {"p":10, "n":30, "b":30, "r":50, "q":90, "k":900}
    fen = board.board_fen()

    w_score = 0
    b_score = 0

    for k,v in white.items():
        w_score += fen.count(k) * v
        # print("kv: ", k, v, "count(k): ", fen.count(k))
    for k,v in black.items():
        b_score += fen.count(k) * v
    # print("w: ", w_score, " b: ", b_score)
    return w_score + b_score

def evaluate(board):
    #does not work
    # white = {"P":10, "N":30, "B":30, "R":50, "Q":90, "K":900}
    # black = {"p":-10, "n":-30, "b":-30, "r":-50, "q":-90, "k":-900}
    #works
    white = {"P":-10, "N":-30, "B":-30, "R":-50, "Q":-90, "K":-900}
    black = {"p":10, "n":30, "b":30, "r":50, "q":90, "k":900}
    fen = board.board_fen()

    w_score = 0
    b_score = 0

    for k,v in white.items():
        w_score += fen.count(k) * v
    for k,v in black.items():
        b_score += fen.count(k) * v
    return w_score + b_score

def minimax(board, depth, turn):
    if (depth == 0):
        return None, evaluate(board)

    possible_moves = list(board.legal_moves)

    values = []
    if (turn == 1):
        max_score = -9999
        max_move = None

        for move in possible_moves:
            temp_board = board.copy()
            temp_board.push(move)
            (_, score) = minimax(temp_board, depth - 1, not turn)

            if (depth == 3):
                print("mv: ", board.san(move), " score: ", score)
                # evaluateRoot(board)
            if score > max_score:
                max_score = score
                max_move = move

        return max_move, max_score

    else:
        min_score = 9999
        min_move = None

        for move in possible_moves:
            temp_board = board.copy()
            temp_board.push(move)
            (_, score) = minimax(temp_board, depth - 1, not turn)

            if (depth == 3):
                print("mv: ", board.san(move), " score: ", score)
                # evaluateRoot(board)
            if score < min_score:
                min_score = score
                min_move = move

        return min_move, min_score




# def print_captured(board):
#     remaining = board.board_fen()
#     white = {'P': 0, 'N': 0, 'B': 0, 'Q': 0, 'K': 0, 'R': 0}
#     black = {'p': 0,'n': 0,'b': 0,'q': 0,'k': 0,'r': 0}
#
#     for k, v in white.items():
#         if k == 'P':
#             white[k] = 8 - remaining.count(k)
#         elif k in ['N','B','R']:
#             white[k] = 2 - remaining.count(k)
#         else:
#             white[k] = 1 - remaining.count(k)
#
#     for k, v in black.items():
#         if k == 'p':
#             black[k] = 8 - remaining.count(k)
#         elif k in ['n','b','r']:
#             black[k] = 2 - remaining.count(k)
#         else:
#             black[k] = 1 - remaining.count(k)
#
#     for k, v in white.items():
#         print(chess.UNICODE_PIECE_SYMBOLS[k] * v, end=' ')
#     print('\n')
#     for k, v in black.items():
#         print(chess.UNICODE_PIECE_SYMBOLS[k] * v, end=' ')
#     # print('\n')

def main():
    board = chess.Board()
    turn = 0
    print(board.unicode())
    print("\n")

    while (not board.is_game_over()):
        if (turn % 2 == 0):
            if board.is_check():
                print("WHITE is in CHECK.")

            while True:
                w_in = input("WHITE's turn: ")
                print("\n")
                try:
                    w_in = board.push_san(w_in)
                except ValueError:
                    print(board.unicode())
                    print("Invalid input, try again.")
                    # print("Legal moves: ")
                    # [print(i) for i in list(board.legal_moves)]
                    continue
                break
        else:
            if board.is_check():
                print("BLACK is in CHECK.")
            # move = player(board)
            move, score = minimax(board, 3, 1)
            print("Black chose: ", board.san(move))
            print("Score: ", score)
            print('\n')
            board.push_uci(move.uci())

        print(board.unicode())
        # print_captured(board)
        print("\n")
        turn += 1
    print("Checkmate!")

    end_game = board.result()
    if end_game == "1-0":
        print("WHITE wins!")
    elif end_game == "0-1":
        print("BLACK wins!")
    else:
        print("It's a DRAW!")

if __name__ == "__main__":
    main()
