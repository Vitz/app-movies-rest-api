# app-movies-rest-api
  
Zadanie rekturacyjne Junior Python Developer (rozwinięte na potrzeby własne).  

Technologie:   
-Python                  3.6.4,  
-Django                  2.0.3,  
-django-bootstrap3       10.0.1,  
-django-filter           2.1.0,  
-django-heroku           0.3.1,  
-django-rest-api         0.1.5.


Lista filmów:  
http://django-rest-api-imdb.herokuapp.com/movies/  

Film za pomocą ID:  {"title": "Tytuł", "score": 5.1, 'genres’: [Comedy], 'link’: 'link do imdb’, 'year’: 2001}  
http://django-rest-api-imdb.herokuapp.com/movie/88/ 
lub  
http://django-rest-api-imdb.herokuapp.com/movies/88/ 

Sortowanie za pomocą parametrów:  
http://django-rest-api-imdb.herokuapp.com/movies/?sort=year 

Wybór za pomocą parametrów:  
http://django-rest-api-imdb.herokuapp.com/movies/?year=2000&genre=Comedy  

Filmy za pomocą listy tagów:  
http://django-rest-api-imdb.herokuapp.com/movies/?tag=funny&tag=animation   

Czyszczenie i ponowne wgranie DB (na HEROKU raczej nie zadziała):  
POST http://django-rest-api-imdb.herokuapp.com/db z body {"source": "ml-latest-small"}  

