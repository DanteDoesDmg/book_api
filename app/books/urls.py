from django.urls import path

from . import views

urlpatterns = [
    path('db', views.get_external_books),
    path('books', views.get_books),
    path('books/<int:book_id>', views.get_books)
]