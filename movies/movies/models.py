from django.db import models
from django.contrib.auth.models import User


class Movies(models.Model):
    movie_id = models.IntegerField(primary_key=True) # the name can be different
    title = models.CharField(max_length=100)
    genres = models.CharField(max_length=100)
    year = models.IntegerField(null=True)

class Links(models.Model):
    movie_id = models.ForeignKey(Movies, on_delete=models.CASCADE, db_column="movie_id")
    imdb_id = models.IntegerField()
    tmdb_id = models.IntegerField(null=True)



class Ratings(models.Model):
    user_id = models.IntegerField()
    movie_id = models.ForeignKey(Movies, on_delete=models.CASCADE, db_column="movie_id")
    RATINGS = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')]
    rating = models.CharField(max_length=1, choices=RATINGS)
    timestamp = models.IntegerField()


class Tags(models.Model):
    user_id = models.IntegerField()
    movie_id = models.ForeignKey(Movies, on_delete=models.CASCADE, db_column="movie_id")
    tag = models.CharField(max_length=100)
    timestamp = models.IntegerField()





