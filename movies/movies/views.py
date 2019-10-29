import csv
import os
from pathlib import Path

import django_filters
import pandas as pandas
import re
import requests
from django.core import serializers
from django.db.backends import sqlite3
from django.db.models import QuerySet
from django.shortcuts import  render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from .models import Links, Movies, Ratings,Tags
from .serializers import MoviesSerializer, LinksSerializer, RatingsSerializer, TagsSerializer, MoviesDetailsSerializer
import zipfile
import shutil
from django.db import connections


class MoviesView(viewsets.ModelViewSet):
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    serializer_class = MoviesSerializer

    def get_queryset(self):
        year_param = self.request.query_params.get('year', None)
        sort_param = self.request.query_params.get('sort', None)
        tags_param = self.request.query_params.getlist('tag', None)
        genres_param = self.request.query_params.get('genre', None)
        if genres_param:
            queryset_genre = Movies.objects.filter(genres__icontains = genres_param)
        else: 
            queryset_genre = Movies.objects.all()
        if year_param:
            queryset_year = Movies.objects.filter(year=year_param)
        else:
            queryset_year = Movies.objects.all()
        if tags_param:
            tags_set = []
            for tag_param in tags_param:
                tags = set(Tags.objects.filter(tag = tag_param))
                id_list_tmp = []
                for tag in tags:
                    id_list_tmp.append(tag.movie_id.movie_id)
                tags_set.append(frozenset(id_list_tmp))
            tags_ids = set(tags_set[0]).intersection(*tags_set[1:])
            queryset_tags = Movies.objects.filter(movie_id__in= tags_ids)
        else:
            queryset_tags = Movies.objects.all()

        queryset = queryset_year & queryset_tags & queryset_genre # merge
        if queryset is None:
            queryset = Movies.objects.all()

        if sort_param: # sort must be the last param, when queryset is finished
            queryset = queryset.order_by(sort_param)
            
        return queryset


class LinksView(viewsets.ModelViewSet):
    queryset = Links.objects.all()
    serializer_class = LinksSerializer


class RatingsView(viewsets.ModelViewSet):
    queryset = Ratings.objects.all()
    serializer_class = RatingsSerializer


class TagsView(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class MovieView(APIView):
    def get(self, request, movie_id):
        movie = Movies.objects.filter(movie_id=movie_id)[0]
        rating = Ratings.objects.filter(movie_id=movie.movie_id)[0]
        link = Links.objects.filter(movie_id=movie.movie_id)[0]
        serializer_movie = MoviesSerializer(movie)
        serializer_rating = RatingsSerializer(rating)
        serializer_link = LinksSerializer(link)
        dict_result = {}

        dict_result["title"] = serializer_movie.data["title"]
        dict_result["score"] = serializer_rating.data["rating"]
        dict_result["genres"] = serializer_movie.data["genres"]
        dict_result["link"] = "https://www.imdb.com/title/tt0"+str(serializer_link.data["imdb_id"])
        dict_result["year"] = str(serializer_movie.data["year"])
        dict_result["rating_avg"] = str(serializer_movie.data["rating_amount"])
        dict_result["rating_amount"] = str(serializer_movie.data["rating_amount"])
        return Response(dict_result)


class DBView(APIView):
    def norm(self, name):
        norm_name = ""
        for letter in name:
            if letter.isupper():
                norm_name += "_"
            norm_name += letter.lower()
        return norm_name

    def year_from_title(self, title):
        year = None
        pattern = re.compile("[(][0-9][0-9][0-9][0-9][)]")
        pattern_only_num = re.compile("[0-9][0-9][0-9][0-9]")
        if title and pattern.search(title):
            print(pattern.search(title).string)
            try: 
                year_str = pattern_only_num.search(pattern.search(title).string)
                year = int(year_str.group(0))
            except:
                print("Pattern (yyyy) found, but yyyy not")
        return year

    def unzip_db(self):
        # Delete old files, unpack zip
        path_unzip = "media/unzip"
        path = "media/ml-latest-small.zip"
        if os.path.exists(path_unzip):
            shutil.rmtree(path_unzip)
        os.mkdir(path_unzip)
        print("Dir prepared")
        zip_ref = zipfile.ZipFile(path, 'r')
        zip_ref.extractall(path_unzip)
        zip_ref.close()
        print("DB unzipped")

    def download_db(self):
        # Download and replace ml-latest-small.zip if file already exists
        url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
        path = "media/ml-latest-small.zip"
        chunk = 2048
        req = requests.get(url, stream=True)
        if req.status_code == 200:
            with open(path + "new", 'wb') as f:
                for chunk in req.iter_content(chunk):
                    f.write(chunk)
                f.close()
        if os.path.exists(path + "new"):
            if os.path.exists(path):
                os.remove(path)
                print("Old zip removed")
            os.rename(path + "new", path)
        print("DB downloaded")

    def load_movies(self, conn):
        entity_name = "movies_movies"
        path_csv = "media/unzip/ml-latest-small/movies.csv"
        print("Now deleting:", entity_name)
        self.delete_entity(entity_name, conn)
        print("Now intesring:", entity_name)
        with open(path_csv, encoding="utf8") as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                print(row)
                new_movie = Movies()
                new_movie.movie_id = int(row[0])
                new_movie.title = row[1]
                new_movie.genres = row[2]
                new_movie.year = self.year_from_title(row[1])
                print(new_movie)
                new_movie.save()

    def load_links(self, conn):
        entity_name = "movies_links"
        path_csv = "media/unzip/ml-latest-small/links.csv"
        print("Now deleting:", entity_name)
        self.delete_entity(entity_name, conn)
        with open(path_csv, encoding="utf8") as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                print(row[0], row[1], row[2] )
                new_link = Links()
                new_link.movie_id = Movies.objects.get(movie_id=int(row[0]))
                new_link.imdb_id = row[1]
                if not row[2]:
                    row[2] = None
                new_link.tmdb_id = row[2]
                new_link.save()

    def load_tags(self, conn):
        entity_name = "movies_tags"
        path_csv = "media/unzip/ml-latest-small/tags.csv"
        print("Now deleting:", entity_name)
        self.delete_entity(entity_name, conn)
        with open(path_csv, encoding="utf8") as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                print(row[0], row[1], row[2], row[3])
                new_tag = Tags()
                new_tag.user_id = row[0]
                new_tag.movie_id = Movies.objects.get(movie_id=int(row[1]))
                new_tag.tag = row[2]
                new_tag.timestamp = row[3]
                new_tag.save()

    def load_ratings(self, conn):
        entity_name = "movies_ratings"
        path_csv = "media/unzip/ml-latest-small/ratings.csv"
        print("Now deleting:", entity_name)
        self.delete_entity(entity_name, conn)
        with open(path_csv, encoding="utf8") as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                print(row[0], row[1], row[2], row[3])
                new_tag = Ratings()
                new_tag.user_id = row[0]
                new_tag.movie_id = Movies.objects.get(movie_id=int(row[1]))
                new_tag.rating = row[2]
                new_tag.timestamp = row[3]
                new_tag.save()

    def post(self, request, format=None):
        if request.body and json.loads(request.body) == {"source": "ml-latest-small"}:
            try:
                conn = connections['default']
                self.download_db()
                self.unzip_db()
                self.load_movies(conn)
                self.load_links(conn)
                self.load_tags(conn)
                self.load_ratings(conn)
                status = "OK"
            except Exception as e:
                print(e)
                print("Unable to reload DB")
                status = "Fail"
        elif request.body and json.loads(request.body) == {"reset": "rating"}:            
            self.add_ratings2movies()    
        else:
            status = "Wrong request"
        return Response({"Status": status})

    def add_ratings2movies(self):
        movies = Movies.objects.all()
        for movie in movies:
            try:
                ratings = Ratings.objects.filter(movie_id = movie.movie_id)
                movie.rating_avg =  ratings.aggregate(Avg('rating'))
                movie.rating_amount =  len(ratings)
                movie.save()
            except:
                movie.rating_avg =  0.0
                movie.rating_amount =  0
                movie.save()            


    def delete_entity(self, entity_name, conn):
        conn.cursor().execute("PRAGMA foreign_keys = OFF;")
        conn.cursor().execute("delete from " + entity_name)
        conn.cursor().execute("PRAGMA foreign_keys = ON;")


