from django.shortcuts import render
from django.http import  Http404
from .models import Album,Song
from django.shortcuts import render
# Create your views here.

def index(request):
    all_album = Album.objects.all()
    context = {"all_album":all_album}
    return render(request,"music/index.html",context)

def details(request,album_id):
    try:
        album = Album.objects.get(pk=album_id)
    except Album.DoesNotExist:
        raise Http404("Album does not exist")
    return render(request,"music/details.html",{"album":album})
