from django.db import models

# Create your models here.

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    google_id = models.CharField(max_length=15, null=True)
    title = models.CharField(max_length=50, null=True)
    categories = models.CharField(max_length=255, null=True)
    published_date = models.DecimalField(max_digits=4, decimal_places=0, null=True)
    authors = models.CharField(max_length=255, null=True)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    ratings_count = models.PositiveIntegerField(null=True)
    thumbnail = models.URLField(null=True)