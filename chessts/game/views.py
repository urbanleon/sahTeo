from django.shortcuts import render
from django.http import HttpResponse

import json

from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def play(request):
    # return HttpResponse("Hello, world! You're at the game index.")
    # data = request.body
    return render(request, 'game/board.html')

@csrf_exempt
def getMove(request):
    output = json.loads(request.body)
    print(output['value'])
    return HttpResponse("get move ok")
    # output = request.body['value']