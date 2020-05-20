from .models import Album,Song
from django.views import generic
from django.views.generic.edit import  CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
# Create your views here.

class IndexView(generic.ListView):
    template_name = "music/index.html"
    context_object_name = "all_album"
    def get_queryset(self):
        return Album.objects.all()

class DetailsView(generic.DetailView):
    model = Album
    template_name = "music/details.html"
    context_object_name = "album"

class CreateAlbum(CreateView):
    model = Album
    fields = ['artist','album_title','genre','album_logo']

class UpdateAlbum(UpdateView):
    model = Album
    fields = ['artist','album_title','genre','album_logo']

class DeleteAlbum(DeleteView):
    model = Album
    success_url = reverse_lazy('music:index')
