from rest_framework import serializers

from .models import Movie, Genre, Director


class DirectorSerializer(serializers.ModelSerializer):

    """
        Serializing director model
    """

    class Meta:
        model = Director


class GenreSerializer(serializers.ModelSerializer):

    """
        Serializing genre model
    """

    class Meta:
        model = Genre


class MovieSerializer(serializers.ModelSerializer):

    """
        Serializing movie model
    """

    director = serializers.CharField()
    genre = serializers.ListField(allow_empty=False)

    class Meta:
        model = Movie
        fields = ('name', 'imdb_score', 'popularity', 'director', 'genre')


class MovieListSerializer(serializers.ModelSerializer):

    """
        Serializing movie model for listing users
    """

    director = serializers.SerializerMethodField('find_director')
    genre = serializers.SerializerMethodField('list_genres')

    class Meta:
        model = Movie
        exclude = ('id',)

    def find_director(self, obj):
        return obj.director.name

    def list_genres(self, obj):
        return obj.genre.all().values_list('name', flat=True)
