from django.shortcuts import render
from django.http import  HttpResponse
from .models import Album,Song
from django.template import loader
# Create your views here.

def index(request):
    all_album = Album.objects.all()
    template = loader.get_template("music/index.html")
    context = {
        "all_album":all_album,
    }
    return HttpResponse(template.render(context,request))

def details(request,album_id):
    return HttpResponse("<h1>Album Id:" + str(album_id) + "</h1>")
