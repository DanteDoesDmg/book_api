import requests
import json
import time
import operator
from functools import reduce

from .models import *
from django.db.models import Q, When
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


def homepage(request):
    return render(request, 'base.html')
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
        'google_ids': set()
    }
    for book in book_list:
        volume_info = book['volumeInfo']
        tmp_book = {
            'google_id': book['id'],
            'title': volume_info['title'] if 'title' in volume_info else None,
            'categories': volume_info['categories'] if 'categories' in volume_info else None,
            'published_date': volume_info['publishedDate'].split('-')[0] if 'publishedDate' in volume_info else None,
            'authors': volume_info['authors'] if 'authors' in volume_info else None,
            'average_rating': volume_info['averageRating'] if 'averageRating' in volume_info else None,
            'ratings_count': volume_info['ratingsCount'] if 'ratingsCount' in volume_info else None,
            'thumbnail': volume_info['imageLinks']['thumbnail'] if 'thumbnail' in volume_info['imageLinks'] else None
        }

        tmp_dict['books'][book['id']] = tmp_book
        tmp_dict['google_ids'].add(book['id'])
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
        JsonResponse: Zwrócona jest informacja o sukcesie lub niepowodzeniu
    """
    try:
        body = request.body.decode('utf-8')

        if body == '':
            return JsonResponse(
                status=400, data={'msg': "Missing body with required parameter 'q'"})
        body = json.loads(request.body.decode('utf-8'))

        if 'q' not in body:
            return JsonResponse(
                status=400, data={'msg': "Request body missing required parameter 'q'"})

        api_books = prepare_books(requests.get(
            f"https://www.googleapis.com/books/v1/volumes?q={body['q']}").json()['items'])

        if len(api_books) == 0:
            return JsonResponse(
                status=400, data={'msg': 'No books that matched provided criteria were found'})

        existing_books = Book.objects.filter(
            google_id__in=api_books['google_ids'])
        existing_books_google_ids = {book.google_id for book in existing_books}

        books_to_create = [
            Book(
                **book) for book in api_books['books'].values()
            if book['google_id'] not in existing_books_google_ids]

        Book.objects.bulk_create(books_to_create)

        if len(existing_books) > 0:
            fields_to_update = set()
            for book in existing_books:
                google_id = book.google_id
                for field_name, field_value in api_books['books'][google_id].items(
                ):
                    fields_to_update.add(field_name)
                    book.__setattr__(field_name, field_value)

            Book.objects.bulk_update(existing_books, fields_to_update)
        if len(books_to_create) > 0:
            return JsonResponse(
                status=201, data={'msg': 'New books were succesfully added to the databasse'})
        else:
            return JsonResponse(
                status=204, data={'msg': 'Succesfully updated books'})

    except BaseException as error:

        return JsonResponse(status=500, data={})


@require_http_methods(["GET"])
def get_books(request, book_id=None):
    """Funkcja zwracająca pojedynczą książkę, lub listę książek, możliwą do filtrowania po
        'published_date' oraz 'authors' oraz sortowaną po 'book_id' lub 'published_date'
        sortowanie i filtrowanie sterowane jest przez get parameters:
            ?author=str: example str - można podać w ""
            ?published_date=int: example int
            ?sort=str - published_date lub -published_date

    Args:
        request (GET): Request zawierająy w url parameters book_id lub opcjonalny zestaw get paramters sterujący
                        sortowaniem i filtrowaniem
        book_id (int, optional): book_id książki którą chce pobrać użytkownik, jeśli nie 
        jest podane pobierana jest lista książek. Defaults to None.

    Returns:
        JsonResponse: Response zawierająca książkę, listę książek lub informację o błędzie
    """    
    try:
        if book_id is not None:
            try:
                book = Book.objects.get(book_id=book_id)

                return JsonResponse(data=model_to_dict(book))
            except ObjectDoesNotExist:
                return JsonResponse(
                    status=404, data={'msg': "Book with provided book_id does not exist"})

        allowed_get_params = ['author', 'published_date', 'sort']

        my_filter = {}          # Defaultowy pusty filtr
        authors_filter = Q()    # Defaultowy Field lookup zwracający wszystkich autorów
        order_by = 'book_id'    # Defaultowy sort bo book_id   

        for param in allowed_get_params:
            if len(request.GET.getlist(param)) != 0:
                if param == 'author':
                    authors = []
                    for author in request.GET.getlist(param):
                        try:
                            authors.append(json.loads(author))
                        except json.decoder.JSONDecodeError:
                            # Na wypadek podania autora w url bez ""
                            authors.append(author)
                    authors_filter = reduce(operator.and_, (Q(
                        authors__icontains=author) for author in authors))

                elif param == 'sort':
                    order_by = [order for order in request.GET.getlist(param)
                                if order in ['-published_date', 'published_date']][0]

                elif param == 'published_date':
                    my_filter['published_date__in'] = request.GET.getlist(
                        param)

        books = Book.objects.filter(
            authors_filter,
            **my_filter
        ).order_by(order_by).values()
        return JsonResponse(data={'books': list(books)})

    except BaseException as err:
        print(err)
        return JsonResponse(data={'msg': "Server error"}, status=500)
