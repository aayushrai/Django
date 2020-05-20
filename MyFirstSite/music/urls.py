from django.urls import path
from . import views

app_name = "music"
urlpatterns = [
    path('',views.IndexView.as_view(),name='index'),
    path('<int:pk>/',views.DetailsView.as_view(),name='details'),
    path('album/add/',views.CreateAlbum.as_view(),name='add-album'),
    path('album/<int:pk>/',views.UpdateAlbum.as_view(),name='update-album'),
    path('album/<int:pk>/delete/',views.DeleteAlbum.as_view(),name='delete-album'),
]