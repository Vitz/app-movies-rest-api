from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from .views import MoviesView
from . import views

router = routers.DefaultRouter()
router.register('movies', views.MoviesView, base_name="MoviesView")
router.register('links', views.LinksView, base_name="LinksViews")
router.register('tags', views.TagsView, base_name="TagsView")
router.register('ratings', views.RatingsView, base_name="RatingsView")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('db/', views.DBView.as_view(), name="db"),
    # path('movie/<int:movie_id>/', views.movie_by_id, name="movie_by_id"),
    path('movie/<movie_id>/', views.MovieView.as_view(), name="movie_by_id"),
    # path('movie/<movie_id>/', views.MovieView.as_view(), name="movie_by_id"),
]
