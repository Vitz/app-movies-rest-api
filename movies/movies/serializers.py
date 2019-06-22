from rest_framework import serializers
from .models import Links, Movies, Ratings,Tags


class MoviesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movies
        fields = ('movie_id', 'title', 'genres')


class LinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Links
        fields = '__all__'


class RatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields = '__all__'

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'





