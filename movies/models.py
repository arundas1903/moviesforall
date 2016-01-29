from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Director(models.Model):
    
    """
        Model for directors
    """

    name = models.CharField(max_length=255, null=False, blank=False)

    def __unicode__(self):
        return self.name


class Genre(models.Model):

    """
        Model for Genre
    """

    name = models.CharField(max_length=255, null=False, blank=False)

    def __unicode__(self):
        return self.name


class Movie(models.Model):

    """
        Model for movies
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    imdb_score = models.FloatField(null=False, blank=False, validators=[
        MinValueValidator(0.0), MaxValueValidator(10.0)])
    popularity = models.FloatField(null=False, blank=False, validators=[
        MinValueValidator(0.0), MaxValueValidator(100.0)])
    director = models.ForeignKey(Director)
    genre = models.ManyToManyField(Genre)

    def __unicode__(self):
        return self.name
