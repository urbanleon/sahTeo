#!/usr/bin/env python3
import chess
import random

def player(board):
    move = random.choice(list(board.legal_moves))
    return move.uci()

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
                print("Invalid input, try again.")
                print("Legal moves: ")
                for i in list(board.legal_moves):
                    print(i)
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
    print("\n")
    turn += 1
print("Game over!")

if not board.turn:
    print("White wins!")
else:
    print("Black wins!")
