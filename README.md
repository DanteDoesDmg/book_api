##Demo link:
http://rchelek.pythonanywhere.com/

Akpliacja używa danych z na podstawie danych znajdujących się na stronie https://www.googleapis.com/books/v1/volumes
Aplikacja posiada proste API umożliwiające wykonanie następujących operacji:

GET /books - lista wszystkich książek (widok pozwala na filtrowanie i sortowanie po roku - przykład : /books?published_date=1995, /books?sort=-published_date)
GET /books?author="Jan Kowalski"&author="Anna Kowalska" - lista książek zadanych autorów
GET /books/<bookId> - wybrana książka 
{
    "book_id: 82,
    "good_id": "YyXoAAAACAAJ",
    "title": "Hobbit czyli Tam i z powrotem",
    "authors": ["J. R. R. Tolkien"],
    "published_date": "2004",
    "categories": [
        "Baggins, Bilbo (Fictitious character)"
      ],
    "average_rating": 5,
    "ratings_count": 2,
    "thumbnail": "http://books.google.com/books/content?id=YyXoAAAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api",
}

POST /db z body np  {"q": "war"}
Ściąga data set z https://www.googleapis.com/books/v1/volumes?q=war
a następnie wrzuca wpisy do bazy danych aplikacji wpisy (aktualizując już istniejące)
