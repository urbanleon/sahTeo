import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from django.shortcuts import render
from django.http import HttpResponse
import sys
sys.path.append('/home/tommy/Code/chess/mychess')
import json
import alpha_beta as ab
import chess
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
board = chess.Board()

@csrf_exempt
def play(request):
    if (request.method == "POST"):
        fen = json.loads(request.body)
        # print(fen['value'])
        board.set_fen(fen['value'])
        # move, score = ab.minimax(board, 3, 1, -10000, 10000)
        move, score = ab.opening(board)
        print(move.uci(), score)
        return HttpResponse(move.uci())
    return render(request, 'game/board.html')
