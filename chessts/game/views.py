from django.shortcuts import render
from django.http import HttpResponse

import json

from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def play(request):
    #FIX ME: change getMove route to this to check if request.method == "POST"
    if (request.method == "POST"):
        output = json.loads(request.body)
        print(output['value'])
        return HttpResponse("this is a test!!!")
    return render(request, 'game/board.html')

@csrf_exempt
def getMove(request):
    output = json.loads(request.body)
    print(output['value'])
    return HttpResponse("this is a test!!!")
    # output = request.body['value']