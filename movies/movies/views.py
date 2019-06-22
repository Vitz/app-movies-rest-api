import csv
import os
from pathlib import Path

import pandas as pandas
import requests
from django.db.backends import sqlite3
from django.shortcuts import  render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from .models import Links, Movies, Ratings,Tags
from .serializers import MoviesSerializer, LinksSerializer, RatingsSerializer, TagsSerializer
import zipfile
import shutil
from django.db import connections
from imdb import IMDb
class MoviesView(viewsets.ModelViewSet):
    queryset = Movies.objects.all()
    serializer_class = MoviesSerializer


class LinksView(viewsets.ModelViewSet):
    queryset = Links.objects.all()
    serializer_class = LinksSerializer

class RatingsView(viewsets.ModelViewSet):
    queryset = Ratings.objects.all()
    serializer_class = RatingsSerializer


class TagsView(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer

class DBView(APIView):

    def norm(self, name):
        norm_name = ""
        for letter in name:
            if letter.isupper():
                norm_name += "_"
            norm_name += letter.lower()
        return norm_name

    def post(self, request, format=None):
        if request.body and json.loads(request.body) == {"source": "ml-latest-small"}:
            url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
            path = "media/ml-latest-small.zip"
            path_data_tsv = "media/tsv"
            dir_name = "ml-latest-small"
            path_unzip = "media/unzip"
            chunk = 2048

            try:
                # Download and replace ml-latest-small.zip if file already exists
                req = requests.get(url, stream=True)
                if req.status_code == 200:
                    with open(path+"new", 'wb') as f:
                        for chunk in req.iter_content(chunk):
                            f.write(chunk)
                        f.close()
                if os.path.exists(path+"new"):
                    if os.path.exists(path):
                        os.remove(path)
                        print("Old zip removed")
                    os.rename(path+"new", path)
                print("DB downloaded")

                # Delete old files, unpack zip
                if os.path.exists(path_unzip):
                    shutil.rmtree(path_unzip)
                os.mkdir(path_unzip)
                print("Dir prepared")
                zip_ref = zipfile.ZipFile(path, 'r')
                zip_ref.extractall(path_unzip)
                zip_ref.close()
                print("DB unzipped")


                # Load years_dataset
                dataset = {}
                with open(path_data_tsv + "/" +'data.txt', encoding="utf8") as txtfile:
                    txtfile.seek(0)
                    reader = csv.reader(txtfile)
                    for row in reader:
                        dataset[row[0]] = row[1]
                print("example:", dataset["0000739"])
                txtfile.close()

                csv_to_edit = path_unzip + "/" + dir_name + "/links.csv"
                os.rename(csv_to_edit, csv_to_edit+"in")
                csv_out = open(csv_to_edit, 'w', encoding="utf8", newline='')
                writer = csv.writer(csv_out)

                try:
                    with open(csv_to_edit+"in", encoding="utf8") as csv_file:
                        csv_file.seek(0)
                        csv_reader = csv.reader(csv_file, delimiter=',')
                        skip_header = next(csv_reader)
                        skip_header.append("year")
                        print(skip_header)
                        writer.writerow([skip_header[0], skip_header[1], skip_header[2], skip_header[3]])
                        for row in csv_reader:
                            try:
                                writer.writerow([row[0], row[1], row[2], dataset[row[1]]])
                                # if row[0] == 11 or row[0] == "60":
                                #     break
                            except:
                                writer.writerow([row[0], row[1], row[2], 0])

                        csv_file.close()
                    csv_out.close()
                    dataset = {}
                except Exception as e:
                    print(e)
                    print("Nie załadowano links")

                # Prepare DB and its settings
                conn = connections['default']

                # Load CSV files to DB, camelCase into _
                dir_with_files = path_unzip + "/" + dir_name
                file_list = os.listdir(dir_with_files)
                for file in file_list:
                    if str(file).endswith(".csv"): # and str(file) == "movies.csv":
                        entity_name = "movies_" + file.replace(".csv", "")
                        print("Now deleting:", entity_name)
                        conn.cursor().execute("delete from " + entity_name)
                        conn.cursor().execute("PRAGMA foreign_keys = OFF")
                        file_path = dir_with_files + "/" + file
                        print("Now adding:", entity_name)
                        with open(file_path, encoding="utf8") as csv_file:
                            csv_file.seek(0)
                            csv_reader = csv.reader(csv_file, delimiter=',')
                            header = next(csv_reader)
                            print("header:", header)
                            norm_header= []
                            for item in header:
                                norm_header.append(self.norm(item))

                            sql_request_prefix = "INSERT INTO " + entity_name + " ( id, "+ " , ".join(norm_header).rstrip() + ") VALUES("
                            #sql_request_prefix = "INSERT INTO " + entity_name + " VALUES("
                            sql_request_postfix = ")"
                            row_iterator = 0
                            for row in csv_reader:
                                items_as_values = "NULL"                                                   ","
                                for i in range(len(row)):
                                    row[i] = row[i].replace("'","''")
                                    if type(row[i]) == type(1):
                                        items_as_values = items_as_values + row[i] + ","
                                    elif type(row[i]) == type("str"):
                                        items_as_values = items_as_values + "'" + row[i] + "',"
                                    else:
                                        raise("Input type is not suported yet")
                                items_as_values = items_as_values.rstrip(',')
                                sql_request = sql_request_prefix+items_as_values+sql_request_postfix

                                print(sql_request)
                                conn.cursor().execute(sql_request)
                                row_iterator = row_iterator + 1
                                # if row_iterator > 100:
                                #     break


                status = "OK"
            except Exception as e:
                print(e)
                print("Unable to reload DB")
                status = "Fail"
        else:
            status = "Wrong request"
        return Response({"Status": status})









