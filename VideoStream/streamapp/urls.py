from django.urls import path, include
from . import views

app_name = "video"
urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('Ipwebcam', views.Ipwebcam, name='Ipwebcam'),
    ]