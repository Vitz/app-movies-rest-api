# app-movies-rest-api

Zadanie rekturacyjne Junior Python Developer.

Technologie:
-Django
-django-rest-framework


Lista filmów:
http://django-rest-api-imdb.herokuapp.com/movies/

Film za pomocą ID:  {"title": "Tytuł", "score": 5.1, 'genres’: [Comedy], 'link’: 'link do imdb’, 'year’: 2001}
http://django-rest-api-imdb.herokuapp.com/movie/88/
lub 
http://django-rest-api-imdb.herokuapp.com/movies/88/

Sortowanie za pomocą parametrów:
http://django-rest-api-imdb.herokuapp.com/movies/?sort=year

Wybór za pomocą parametrów:
http://django-rest-api-imdb.herokuapp.com/movies/?year=2000

Filmy za pomocą listy tagów:
http://django-rest-api-imdb.herokuapp.com/movies/?tag=funny&tag=animation

Czyszczenie i ponowne wgranie DB (na HEROKU raczej nie zadziała):
POST http://django-rest-api-imdb.herokuapp.com/db z body {"source": "ml-latest-small"}
