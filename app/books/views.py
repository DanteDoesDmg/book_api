import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
# Create your views here.

@require_http_methods(["POST"])
def get_external_books(request):

    try:

        body = json.loads(request.body.decode('utf-8'))

        new_books = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={body['q']}").json()['items']


        return JsonResponse(data=new_books, safe=False)
    except BaseException as error:
        return JsonResponse(data={})