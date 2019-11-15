from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static



from .views import MoviesView
from . import views
from . import viewsDB

router = routers.DefaultRouter()
router.register('movies', views.MoviesView.as_view(), base_name="MoviesView")
router.register('links', views.LinksView, base_name="LinksViews")
router.register('tags', views.TagsView, base_name="TagsView")
router.register('ratings', views.RatingsView, base_name="RatingsView")
router.register('seasons', views.SeasonsViews, base_name="SeasonsView")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('movies/', views.MoviesView.as_view(), name="db"),
    path('', include(router.urls)),
    path('db/', viewsDB.DBView.as_view(), name="db"),
    path('movie/<movie_id>/', views.MovieView.as_view(), name="movie_by_id"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
