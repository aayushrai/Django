from django.shortcuts import render
from django.http import  HttpResponse
from .models import Album,Song

# Create your views here.

def index(request):
    all_album = Album.objects.all()
    html = ""
    for album in all_album:
        url = "/music/" + str(album.id) + "/"
        html += '<a href=' + url + '>' + album.album_title + '</a><br>'
    return HttpResponse(html)

def details(request,album_id):
    return HttpResponse("<h1>Album Id:" + str(album_id) + "</h1>")
