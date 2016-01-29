from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializers import MovieSerializer, MovieListSerializer
from .models import Movie, Genre, Director
from app_user.permissions import IsAdminUser


class Movies(generics.GenericAPIView):

    """
        API to create and view movies.
        * IsAdminUser permission is set for POST as movies can be created
          by admins only.
        * Login as admin and use the token for adding movies. (/user/login_token/)
        * URL: /movies/
        * METHOD: POST
        * Headers:
            - Content-Type: Application/Json
            - Authorization: Token <token> (Space after Token is required)
        * MovieSerializer is used for field validations.
        * Data example:
            - {"name":"Movie name", "director": "Director Name","imdb_score":8.5,"popularity": 85, "genre":
             ["<Genre 1>", "<Genre 2>"]}
        * If a movie is already created new movie will not be created
    """

    queryset = Movie.objects.all()
    permission_classes = (permissions.IsAuthenticated,
                          IsAdminUser)

    def post(self, request, *args, **kwargs):
        data = request.data
        movie_serializer = MovieSerializer(data=data)
        if movie_serializer.is_valid():
            movie = Movie.objects.filter(name=data['name']).first()
            # Checks if movie exists
            if movie:
                return Response({'status': -1, 'errors': 'Movie already exists'})
            director_name = data['director']
            genres = data['genre']
            del data['director']
            del data['genre']
            # Save movie data
            movie = Movie(**data)
            # Create director if not existing
            director = Director.objects.get_or_create(name=director_name)
            movie.director = director[0]
            movie.save()
            for genre_name in genres:
                # Create genre if not existing
                genre = Genre.objects.get_or_create(name=genre_name)
                movie.genre.add(genre[0])
            return Response({'status': 1})
        return Response({'status': -1, 'errors': movie_serializer.errors})


class ViewMovies(generics.GenericAPIView):

    """
        API to view all movies
        * Any logged in user can view movies
        * Login as user and use the token for viewing movies. (/user/login_token/)
        * URL: /movies/list/
            - With pagination: /movies/list/?page=2
        * METHOD: GET
        * Headers:
            - Content-Type: Application/Json
            - Authorization: Token <token> (Space after Token is required)
        * Pagination is done. Query param: page
            - If no page param lists first 10 results (/movies/list/)
        * No.of results per page is set in settings.REST_FRAMEWORK
        Query params:
            1. sort: name/director_name/imdb_score
            2. sort_criteria: asc/desc
    """

    queryset = Movie.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MovieListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        movie_queryset = MovieSort().movie_sorting(request, queryset)
        paginated_queryset = self.paginate_queryset(movie_queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return Response({"status": 1, "count": queryset.count(), "movies": serializer.data})


class UpdateMovie(generics.GenericAPIView):

    """
        Api to update and delete a particular movie
        * IsAdminUser permission is set as movies can be updated or deleted
          by admins only.
        * Login as admin and use the token for updating or deleting movies. (/user/login_token/)
        * URL: /movies/<id>/
        * METHOD: PUT/ DELETE
        * Headers:
            - Content-Type: Application/Json
            - Authorization: Token <token> (Space after Token is required)
        * Data example for updating:
            - {"name":"Movie name", "director": "Director Name","imdb_score":8.5,"popularity": 85, "genre":
             ["<Genre 1>", "<Genre 2>"]}
            - No data for deletion
    """

    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    permission_classes = (permissions.IsAuthenticated,
                          IsAdminUser)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        data = request.data
        movie_instance = self.get_object()
        serializer = self.get_serializer(movie_instance, data=request.data)
        if serializer.is_valid():
            movie_instance.name = data['name']
            movie_instance.imdb_score = data['imdb_score']
            movie_instance.popularity = data['popularity']
            director = Director.objects.get_or_create(name=data['director'])
            movie_instance.director = director[0]
            movie_instance.save()
            movie_instance.genre.all().delete()
            for genre_name in data['genre']:
                # Create genre if not existing
                genre = Genre.objects.get_or_create(name=genre_name)
                movie_instance.genre.add(genre[0])
            return Response({"status": 1})
        return Response({"status": -1, "errors": serializer.errors})

    def delete(self, request, *args, **kwargs):
        movie = self.get_object()
        movie.delete()
        return Response({"status": 1})


class MovieDetail(generics.GenericAPIView):

    """
        Api to view a particular movie
        * Any logged in user can view movies
        * Login as user and use the token for viewing movies. (/user/login_token/)
        * URL: /movies/<id>/
        * METHOD: GET
        * Headers:
            - Content-Type: Application/Json
            - Authorization: Token <token> (Space after Token is required)
    """

    serializer_class = MovieListSerializer
    queryset = Movie.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.detail(request, *args, **kwargs)

    def detail(self, request, *args, **kwargs):
        movie = self.get_object()
        movie_serializer = self.get_serializer(movie)
        return Response({"status": 1, "movie": movie_serializer.data})


class MovieSearch(generics.GenericAPIView):

    """
        Api for movie search.
        * Any logged in user can search for user.
        * Keyword search can be done for name, director or genre.
        * Sorting can be done based on movie name (Asc/ Desc),
          imdb_score (low to high and high to low),
          director name (Asc/ Desc)
        * URL: /movies/search/
            - Query params:
                1. keyword: search keyword
                2. type: name/director/genre
                3. page: page number
                4. sort: name/director_name/imdb_score
                5. sort_criteria: asc/desc
            - Example: /movies/search/?keyword=George&type=director&
              sort=name&sort_criteria=asc&page=2
    """

    queryset = Movie.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MovieListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        movie_queryset = self.get_queryset()
        user_keyword = request.query_params.get('keyword')
        search_type = request.query_params.get('type')
        if user_keyword:
            if search_type == 'name':
                movie_queryset = movie_queryset.filter(name__icontains=user_keyword)
            if search_type == 'director':
                movie_queryset = movie_queryset.filter(director__name__icontains=user_keyword)
            if search_type == 'genre':
                movie_queryset = movie_queryset.filter(genre__name__icontains=user_keyword)
        movie_queryset = MovieSort().movie_sorting(request, movie_queryset)
        paginated_queryset = self.paginate_queryset(movie_queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return Response({"status": 1, "movies": serializer.data, "count": movie_queryset.count()})


class MovieSort(object):

    """
        Class to sort movies
    """

    def movie_sorting(self, request, queryset):
        sort_param = request.query_params.get('sort')
        sort_criteria = request.query_params.get('sort_criteria')
        if sort_param == 'name':
            if sort_criteria == 'desc':
                queryset = queryset.order_by('-name')
            else:
                queryset = queryset.order_by('name')
        if sort_param == 'director_name':
            if sort_criteria == 'desc':
                queryset = queryset.order_by('-director__name')
            else:
                queryset = queryset.order_by('director__name')
        if sort_param == 'imdb_score':
            if sort_criteria == 'desc':
                queryset = queryset.order_by('-imdb_score')
            else:
                queryset = queryset.order_by('imdb_score')
        return queryset
