from django.conf.urls import url

from .views import Movies, ViewMovies, UpdateMovie, MovieDetail, MovieSearch

urlpatterns = [
    url(r'^$', Movies.as_view(), name="movies"),
    url(r'^(?P<pk>[0-9]+)/$', UpdateMovie.as_view()),
    url(r'^(?P<pk>[0-9]+)/view/$', MovieDetail.as_view()),
    url(r'^list/$', ViewMovies.as_view(), name="movies"),
    url(r'^search/$', MovieSearch.as_view()),
]