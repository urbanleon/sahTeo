import sys
import os
from pathlib import Path
sys.path.append(r"C:\Code\Licenta\chess")

# Setup path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from chess.engine import SimpleEngine, Limit

STOCKFISH = SimpleEngine.popen_uci(
    r"C:\Code\Licenta\stockfish\stockfish-windows-x86-64-avx2.exe"
)


from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


import json
import chess
import chess.engine
import alpha_beta as ab

# Global board instance
board = chess.Board()

# === MAIN GAME VIEW ===
def get_board_from_session(request):
    fen = request.session.get("board_fen", chess.STARTING_FEN)
    b = chess.Board(fen)
    return b

def save_board_to_session(request, board):
    request.session["board_fen"] = board.fen()


@csrf_exempt
def play(request):
    if request.method == "POST":
        data = json.loads(request.body)
        fen = data.get("value")
        board.set_fen(fen)

        from alpha_beta import opening  # motorul tău custom
        if board.turn == chess.WHITE:
            move, _ = opening(board)
        else:
            move = chess.Move.from_uci(get_stockfish_move(fen))

        return HttpResponse(move.uci())

    return render(request, "game/board.html")

@csrf_exempt
def auto_play(request):
    if request.method == "POST":
        data = json.loads(request.body)
        fen = data.get("fen", None)

        if not fen:
            return JsonResponse({"error": "No FEN provided"}, status=400)

        board = chess.Board(fen)
        
        # Configurează corect calea către Stockfish!
        engine = chess.engine.SimpleEngine.popen_uci("C:\\Code\\Licenta\\stockfish\\stockfish-windows-x86-64-avx2.exe")

        result = engine.play(board, chess.engine.Limit(time=0.1))
        engine.quit()

        return JsonResponse({"move": result.move.uci()})
    return JsonResponse({"error": "Invalid request"}, status=400)

# === RESTART GAME ===
@csrf_exempt
@require_POST
def restart_game(request):
    global board
    board.reset()
    request.session["board_fen"] = board.fen()
    return HttpResponse("Game restarted")


# === SWITCH SIDES ===
@csrf_exempt
@require_POST
def switch_sides(request):
    global board
    board.reset()

    current = request.session.get("player_color", "white")
    new_color = "black" if current == "white" else "white"
    request.session["player_color"] = new_color

    # Engine plays first move if user is Black
    if new_color == "black":
        move, _ = ab.minimax(board, 3, board.turn, -10000, 10000)
        if move:
            board.push(move)


    request.session["board_fen"] = board.fen()
    return JsonResponse({"color": new_color})


# === SHOW SCORE ===
@csrf_exempt
def score_view(request):
    fen = request.session.get("board_fen", chess.STARTING_FEN)
    temp_board = chess.Board(fen)

    if temp_board.is_checkmate():
        winner = "Black" if temp_board.turn == chess.WHITE else "White"
        result = f"{winner} has checkmated."
    elif temp_board.is_stalemate():
        result = "Stalemate (Draw)"
    else:
        result_obj = STOCKFISH.analyse(temp_board, Limit(time=0.1))
        score = result_obj["score"].white().score(mate_score=10000)

        if score is None:
            result = "Inconclusive"
        elif score > 300:
            result = "White is winning"
        elif score > 50:
            result = "White has advantage"
        elif score < -300:
            result = "Black is winning"
        elif score < -50:
            result = "Black has advantage"
        else:
            result = "Equal"

    return JsonResponse({"score": result})



@csrf_exempt
def undo_move(request):
    if request.method == "POST":
        board = get_board_from_session(request)

        if board.move_stack:
            board.pop()  # Undo last move
            if board.move_stack:
                board.pop()  # Try to undo previous move too
            save_board_to_session(request, board)
            return JsonResponse({ "fen": board.fen() })
        else:
            return JsonResponse({ "error": "No moves to undo." }, status=400)
    return JsonResponse({ "error": "Invalid method" }, status=405)

