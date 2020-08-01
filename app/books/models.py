from django.db import models

# Create your models here.

class Book(models.Model):
    book_id = models.CharField(max_length=15, primary_key=True)
    title = models.CharField(max_length=50)
    published_date = models.DecimalField(max_digits=4, decimal_places=0)
    authors = models.ArrayField(models.CharField(max_length=50))
    average_rating = models.DecimalField(max_digits=2, decimal_places=1)
    ratings_count = models.PositiveIntegerField()
    thumbnail_link = models.URLField()