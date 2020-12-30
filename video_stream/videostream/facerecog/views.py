from django.shortcuts import render
from django.http.response import StreamingHttpResponse
import time
import face_recognition
from imutils.video import VideoStream
import cv2,os
# Create your views here.


def index(request):
	context ={}
	return render(request,"facerecog/video.html", context)

def framesGenerator(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def videoStream(request,ip):
    url = 0
    if "." in ip:
        url = "http://" + ip + "/video"
    camera = VideoCamera(url)
    return StreamingHttpResponse(framesGenerator(camera),
                        content_type='multipart/x-mixed-replace; boundary=frame')

load_encodings = False
face_cascade = cv2.CascadeClassifier(os.getcwd() + '/facerecog/assets/haarcascade_frontalface_default.xml')
known_names,known_faces = [],[]
load_encodings =False
class VideoCamera():

    def __init__(self,url):
        global load_encodings
        self.url = url
        self.video=VideoStream(src=self.url).start()
        if not load_encodings:
            VideoCamera.update_encoding()
            load_encodings=True

    @staticmethod
    def update_encoding():
        global known_names,known_faces,face_cascade
        known_names=[]
        known_faces=[]
        print("Loading Encoding")
        base = os.path.join(os.getcwd(),"facerecog","faces")
        for folder in os.listdir(base):
            for img_name in os.listdir(os.path.join(base,folder)):
                print(os.path.join(base,folder,img_name))
                image = face_recognition.load_image_file(os.path.join(base,folder,img_name))
                location = []
                faces = face_cascade.detectMultiScale(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 1.05, 5)
                for (x,y,w,h) in faces:
                    (startX, startY, endX, endY) = x,y,x+w,y+h
                    if (startX + 5 < endX) and (startY + 5 < endY): 
                            location.append((startY,endX,endY,startX))
                if len(location)>0:
                    encoding = face_recognition.face_encodings(image, known_face_locations=location)[0]
                    known_faces.append(encoding)
                    known_names.append(folder)
                else:
                    print(folder,img_name,": Face not found in image" )

    def __del__(self):
        self.video.stop()

    def face_detection(self,image):
        rects = []
        self.face_cascade = cv2.CascadeClassifier('facerecog/assets/haarcascade_frontalface_default.xml')
        faces = self.face_cascade.detectMultiScale(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 1.05, 5)
        for (x,y,w,h) in faces:
            (startX, startY, endX, endY) = x,y,x+w,y+h
            if (startX + 5 < endX) and (startY + 5 < endY): 
                    rects.append((startY,endX,endY,startX))
        return rects


    def face_recog(self):
        global known_names,known_faces
        image = self.frame
        image2 = self.frame.copy()
        #locations = face_recognition.face_locations(image2, number_of_times_to_upsample=3,model="hog")
        rects = self.face_detection(image2)
        encodings = face_recognition.face_encodings(image2, rects)
        
        for face_encoding, face_location in zip(encodings, rects):
            (startY,endX,endY,startX) = face_location
            crop_image=image2[startY-40:endY+40,startX-40:endX+40,:]
            crop_image_H,crop_image_W,crop_image_C=crop_image.shape
            if crop_image_H>100 and crop_image_W>100:
                face_rect = self.face_detection(crop_image)
                if len(face_rect)==1:
                    results = face_recognition.compare_faces(known_faces, face_encoding,tolerance=0.6)
                    distance = face_recognition.face_distance(known_faces,face_encoding)
                    if True in results:
                        match = known_names[results.index(True)]
                        print(f"Match Found:", {match})
                    else:
                        match = "Unknown"
            

                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])

                    color = [0, 255, 0]

                    cv2.rectangle(image, top_left, bottom_right, 1)

                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])

                    cv2.rectangle(image, top_left, bottom_right,(0,0,255),2)
                    cv2.putText(image, match, (face_location[3], face_location[2]+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def get_frame(self):
        self.frame = self.video.read()

        if self.frame.shape:
            self.face_recog()
        ret, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()
