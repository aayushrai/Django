from django.urls import path
from . import views

app_name = "music"
urlpatterns = [
    path('',views.IndexView.as_view(),name='index'),
    path('<int:pk>/',views.DetailsView.as_view(),name='details'),
    path('album/add/',views.CreateAlbum.as_view(),name='album-add'),
]