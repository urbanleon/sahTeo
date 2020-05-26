from django.shortcuts import render
from django.http import HttpResponse

import json

from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def play(request):
    #FIX ME: change getMove route to this to check if request.method == "POST"
    return render(request, 'game/board.html')

@csrf_exempt
def getMove(request):
    output = json.loads(request.body)
    print(output['value'])
    return HttpResponse("get move ok")
    # output = request.body['value']