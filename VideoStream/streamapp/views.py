from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from .camera import VideoCamera
# Create your views here.

def index(request):
	return render(request, 'streamapp/home.html')

def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
	return StreamingHttpResponse(gen(VideoCamera(0)),content_type='multipart/x-mixed-replace; boundary=frame')

def webcam_feed(request):
	#link = "http://192.168.43.1:8080/video"
	link = str(request.POST["link"])
	return StreamingHttpResponse(gen(VideoCamera(link)),content_type='multipart/x-mixed-replace; boundary=frame')

def ipweblink(request):
	return render(request,"streamapp/ipwebcam.html")


