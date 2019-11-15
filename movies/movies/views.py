import csv
import os
from pathlib import Path

from django.db.models import Avg
import django_filters
import pandas as pandas
import re
import requests
from django.core import serializers
from django.db.backends import sqlite3
from django.db.models import QuerySet
from django.shortcuts import  render
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, generics
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from .models import Links, Movies, Ratings,Tags, Seasons
from .serializers import MoviesSerializer, LinksSerializer, RatingsSerializer, TagsSerializer, MoviesDetailsSerializer, SeasonsSerializer
import zipfile
import shutil
from django.db import connections


class MoviesView(generics.ListAPIView):
    queryset = Movies.objects.all()
    serializer_class = MoviesSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_fields = '__all__'   
    ordering_fields = '__all__' 

    def get_queryset(self):
        genres_param = self.request.query_params.get('genre', None)
        if genres_param:
            queryset_genre = Movies.objects.filter(genres__icontains = genres_param)
        else: 
            queryset_genre = Movies.objects.all()
        return queryset_genre

    # def get_queryset(self):
    #     year_param = self.request.query_params.get('year', None)
    #     sort_param = self.request.query_params.get('sort', None)
    #     tags_param = self.request.query_params.getlist('tag', None)
    #     genres_param = self.request.query_params.get('genre', None)
    #     if genres_param:
    #         queryset_genre = Movies.objects.filter(genres__icontains = genres_param)
    #     else: 
    #         queryset_genre = Movies.objects.all()
    #     if year_param:
    #         queryset_year = Movies.objects.filter(year=year_param)
    #     else:
    #         queryset_year = Movies.objects.all()
    #     if tags_param:
    #         tags_set = []
    #         for tag_param in tags_param:
    #             tags = set(Tags.objects.filter(tag = tag_param))
    #             id_list_tmp = []
    #             for tag in tags:
    #                 id_list_tmp.append(tag.movie_id.movie_id)
    #             tags_set.append(frozenset(id_list_tmp))
    #         tags_ids = set(tags_set[0]).intersection(*tags_set[1:])
    #         queryset_tags = Movies.objects.filter(movie_id__in= tags_ids)
    #     else:
    #         queryset_tags = Movies.objects.all()

    #     queryset = queryset_year & queryset_tags & queryset_genre # merge
    #     if queryset is None:
    #         queryset = Movies.objects.all()

    #     if sort_param: # sort must be the last param, when queryset is finished
    #         queryset = queryset.order_by(sort_param)
            
    #     return queryset


class SeasonsViews(viewsets.ModelViewSet):
    queryset = Seasons.objects.all()
    serializer_class = SeasonsSerializer

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
        link = Links.objects.filter(movie_id=movie.movie_id)[0]
        serializer_movie = MoviesSerializer(movie)
        serializer_link = LinksSerializer(link)
        dict_result = {}

        dict_result["title"] = serializer_movie.data["title"]
        dict_result["genres"] = serializer_movie.data["genres"]
        dict_result["imdb"] = "https://www.imdb.com/title/tt0"+str(serializer_link.data["imdb_id"])
        dict_result["year"] = str(serializer_movie.data["year"])
        dict_result["rating_avg"] = str(serializer_movie.data["rating_avg"])
        dict_result["rating_amount"] = str(serializer_movie.data["rating_amount"])
        return Response(dict_result)

