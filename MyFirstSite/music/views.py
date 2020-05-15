from .models import Album,Song
from django.shortcuts import render,get_object_or_404
# Create your views here.

def index(request):
    all_album = Album.objects.all()
    context = {"all_album":all_album}
    return render(request,"music/index.html",context)

def details(request,album_id):
   # album = Album.objects.get(pk=album_id)
    album = get_object_or_404(Album, pk=album_id)
    return render(request,"music/details.html",{"album":album})

def favorite(request,album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        song = album.song_set.get(pk=request.POST["song"])
    except (KeyError,Song.DoesNotExist):
        return render(request, "music/details.html", {"album": album,"error:message":"You did not select valid song"})
    else:
        song.is_favorite =True
        song.save()
        return render(request, "music/details.html", {"album": album})