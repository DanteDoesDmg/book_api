import requests
import json
import time
from .models import *

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
# Create your views here.


def prepare_books(book_list):
    """Funkcja przyjmuje jako argument listę książek z zapytania GET na 
    https://www.googleapis.com/books/v1/volumes?q=somestring, następnie
    przetwarza ją na dict zawierajacy kluczowe dane każdej książki oraz
    set id wszyskich pobranych książek

    Args:
        book_list (list): lista książek znajdujących się pod atrybutem items zapytania
        GET na adres https://www.googleapis.com/books/v1/volumes?q=somestring


    """    
    tmp_dict = {
        'books': {},
        'book_ids': set()
    }
    for book in book_list:
        volume_info = book['volumeInfo']
        tmp_book = {
            'book_id': book['id'],
            'categories': json.dumps(
                volume_info['categories']) if 'categories' in volume_info else None,
            'published_date': volume_info['publishedDate'].split('-')[0] if 'publishedDate' in volume_info else None,
            'authors': json.dumps(volume_info['authors']) if 'authors' in volume_info else None,
            'average_rating': volume_info['averageRating'] if 'averageRating' in volume_info else None,
            'ratings_count': volume_info['ratingsCount'] if 'ratingsCount' in volume_info else None,
            'thumbnail_link': volume_info['imageLinks']['thumbnail'] if 'thumbnail' in volume_info else None
        }

        tmp_dict['books'][book['id']] = tmp_book
        tmp_dict['book_ids'].add(book['id'])
    return tmp_dict


@require_http_methods(["POST"])
def get_external_books(request):
    """Funkcja tworzy i aktualizuje książki w bazie danych na podstawie
    zapytania get na adres: https://www.googleapis.com/books/v1/volumes?q=q
    gdzie paramater q pobierany jest z POST request na adres
    /db POST request z body w formie {'q': string}

    Args:
        request ([POST]): Post z body w formie {'q': string}

    Returns:
        JsonResponse: Zwrócona jest informacja o sukcesie 
    """
    try:
        body = json.loads(request.body.decode('utf-8'))
        api_books = prepare_books(requests.get(
            f"https://www.googleapis.com/books/v1/volumes?q={body['q']}").json()['items'])

        existing_books = Book.objects.filter(book_id__in=api_books['book_ids'])
        existing_books_ids = {book.book_id for book in existing_books}

        books_to_create = [
            Book(
                **book) for book in api_books['books'].values()
                    if book['book_id'] not in existing_books_ids]

        Book.objects.bulk_create(books_to_create)

        fields_to_update = set()
        for book in existing_books:
            book_id = book.book_id
            for field_name, field_value in api_books['books'][book_id].items():
                fields_to_update.add(field_name)
                book.__setattr__(field_name, field_value)

        fields_to_update.remove('book_id')
        Book.objects.bulk_update(existing_books, fields_to_update)
        return JsonResponse(data={})

    except BaseException as error:
        return JsonResponse(status=500, data={})
