
from django.urls import include, path

from movies.movies.views import HomeRender

urlpatterns = [
    path('', include('movies.movies.urls')),
]