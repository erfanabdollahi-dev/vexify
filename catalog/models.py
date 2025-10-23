from contextlib import nullcontext
from accounts.models import  User
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField(max_length=200, blank=True, null=True)
    cover = models.ImageField(upload_to='categories/')


    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=80)
    bio = models.TextField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='artists/', blank=True, null=True)

    def __str__(self):
        return self.name

class Album(models.Model):
    name = models.CharField(max_length=80)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='albums', blank=True)
    cover = models.ImageField(upload_to='albums/')
    release_date = models.DateField()

    def __str__(self):
        return self.name



class Song(models.Model):
    name = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, related_name='songs', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, related_name='songs', on_delete=models.SET_NULL, blank=True, null=True)
    cover = models.ImageField(upload_to='songs/', null=True, blank=True)
    audio_file = models.FileField(upload_to='audio_file/')
    duration = models.DurationField(blank=True, null=True)
    popularity = models.PositiveIntegerField(default=0)
    release_date = models.DateField()

    def __str__(self):
        return self.name

class Playlist(models.Model):
    name = models.CharField(max_length=80)
    user = models.ForeignKey(User,related_name='playlists', on_delete=models.CASCADE)
    songs= models.ManyToManyField(Song, related_name='playlists')
    cover = models.ImageField(upload_to='playlists/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, related_name='favorites')
    albums = models.ManyToManyField(Album, related_name='favorited_by', blank=True)
    playlists = models.ManyToManyField(Playlist, related_name='favorited_by', blank=True)
    artists = models.ManyToManyField(Artist, related_name='favorited_by', blank=True)

    def __str__(self):
        return f"{self.user.username}'s favorites"

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"