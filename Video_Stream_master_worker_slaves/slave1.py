import os
import face_recognition
from flask import Flask, request
import cv2
import base64
import numpy as np
import os
import face_recognition
from imutils.video import VideoStream
import time
import datetime
import requests
import threading
from collections import deque

app = Flask(__name__)

load_encodings = False
face_cascade = cv2.CascadeClassifier(os.getcwd() + '/haarcascade_frontalface_default.xml')
known_names,known_faces = [],[]

class FaceRecog:
    
    def __init__(self):
        global load_encodings
        self.qSize = 8
        self.faceRecogQ = deque(maxlen=self.qSize)
        self.counter = 0
        if not load_encodings:
            FaceRecog.update_encoding()
            load_encodings=True
    
    @staticmethod
    def update_encoding():
        global known_names,known_faces,face_cascade
        known_names=[]
        known_faces=[]
        print("Loading Encoding")
        base = os.path.join(os.getcwd(),"Faces")
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
    
    def face_detection(self,image):
        rects = []
        self.face_cascade = cv2.CascadeClassifier(os.getcwd() + '/haarcascade_frontalface_default.xml')
        faces = self.face_cascade.detectMultiScale(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 1.05, 5)
        for (x,y,w,h) in faces:
            (startX, startY, endX, endY) = x,y,x+w,y+h
            if (startX + 5 < endX) and (startY + 5 < endY): 
                    rects.append((startY,endX,endY,startX))
        return rects


    def face_recog(self,frame,camera_name,timestamp,starttime,service):
        global known_names,known_faces
        image = frame
        image2 = frame.copy()
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
                        print(f"Match Found:", {match}," in camera::",camera_name , " and time taken by face recog is ",time.time() - starttime)
                    else:
                        match = "Unknown"
                        print("Unknown found in camera::",camera_name ," and time taken by face recog is ",time.time() - starttime)
                        
                    self.faceRecogQ.append(match)
                    url = "http://127.0.0.1:7001/data"
                    
                    if self.counter%self.qSize==0:
                        flag,name = self.checkFaceRecogQ()
                        if flag:
                            data = {"camera":camera_name,"face":name,"timestamp":timestamp,"service":service}
                            requests.post(url,data=data)
                            print("-"*40)
                            print("Sent to master for database update")
                            print("-"*40)
                        self.counter = 0
                    self.counter += 1
                    
                    
    
    def checkFaceRecogQ(self):
        for name in self.faceRecogQ:
            if name != self.faceRecogQ[0]:
                return [False,None]
        return [True,self.faceRecogQ[0]]
        
                
    def get_frame(self,frame,camera_name,timestamp,service):
        if frame.shape:
            starttime = time.time()
            self.face_recog(frame,camera_name,timestamp,starttime,service)
            

face_r = FaceRecog()

@app.route("/", methods=["POST"])
def home():
    camera_name = request.form.get("camera")
    img = request.form.get("image")
    timestamp = request.form.get("timestamp")
    service = request.form.get("service")
    jpg_original = base64.b64decode(img)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    image_buffer = cv2.imdecode(jpg_as_np, flags=1)
    # t1 = threading.Thread(target=face_r.get_frame,args=[image_buffer,camera_name,timestamp])
    # t1.start()
    face_r.get_frame(image_buffer,camera_name,timestamp,service)
    return 'Success!'

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True,port="6000",threaded=True)