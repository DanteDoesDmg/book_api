from django.urls import path

from . import views

urlpatterns = [
    path('db/', views.get_external_books),
]