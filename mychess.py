#!/usr/bin/env python3
import chess
import random

def player(board):
    move = random.choice(list(board.legal_moves))
    return move.uci()

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

    for k, v in white.items():
        print(chess.UNICODE_PIECE_SYMBOLS[k] * v, end=' ')
    print('\n')
    for k, v in black.items():
        print(chess.UNICODE_PIECE_SYMBOLS[k] * v, end=' ')
    # print('\n')


board = chess.Board()
turn = 0
print(board.unicode())
print("\n")

while (not board.is_game_over()):
    if (turn % 2 == 0):
        while True:
            w_in = input("WHITE's turn: ")
            print("\n")
            try:
                w_in = board.push_san(w_in)
            except ValueError:
                print(board.unicode())
                print("Invalid input, try again.")
                print("Legal moves: ")
                [print(i) for i in list(board.legal_moves)]
                continue
            break
    else:
        move = player(board)
        board.push_uci(move)
        print("Black chose: ", move)
        print('\n')
        # while True:
        #     b_in = input("BLACK's turn: ")
        #     print("\n")
        #     try:
        #         b_in = board.push_san(b_in)
        #     except ValueError:
        #         print("Invalid input, try again.")
        #         print("Legal moves: ")
        #         for i in list(board.legal_moves):
        #             print(i)
        #         continue
        #     break

    print(board.unicode())
    print_captured(board)
    print("\n")
    turn += 1
print("Game over!")

end_game = board.result()
if end_game == "1-0":
    print("WHITE wins!")
elif end_game == "0-1":
    print("BLACK wins!")
else:
    print("It's a DRAW!")
