from django.db import models
from django.urls import reverse

class Album(models.Model):
    artist = models.CharField(max_length=50)
    album_title = models.CharField(max_length=50)
    genre = models.CharField(max_length=30)
    album_logo = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('music:details',kwargs={"pk":self.pk})

    def __str__(self):
        return self.album_title + ' - ' + self.artist

class Song(models.Model):
    album = models.ForeignKey(Album,on_delete=models.CASCADE)
    file_type = models.CharField(max_length=100 )
    song_title = models.CharField(max_length=100)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.song_title

