from django.shortcuts import render
from django.http import HttpResponse
import sys
sys.path.append('/home/tommy/Code/chess/mychess')
import json
import alpha_beta as ab
import chess
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def play(request):
    if (request.method == "POST"):
        fen = json.loads(request.body)
        # print(fen['value'])
        board = chess.Board()
        board.set_fen(fen['value'])
        move, score = ab.minimax(board, 3, 1, -10000, 10000)
        return HttpResponse(move.uci())
    return render(request, 'game/board.html')
