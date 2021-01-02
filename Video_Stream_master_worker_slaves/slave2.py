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

app = Flask(__name__)

load_encodings = False
face_cascade = cv2.CascadeClassifier(os.getcwd() + '/haarcascade_frontalface_default.xml')
known_names,known_faces = [],[]

class FaceRecog:
    
    def __init__(self):
        global load_encodings
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


    def face_recog(self,frame):
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
                        print(f"Match Found:", {match}," in camera ")
                    else:
                        match = "Unknown"
                        print("Unknown found")
            

                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])

                    color = [0, 255, 0]

                    cv2.rectangle(image, top_left, bottom_right, 1)

                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])

                    cv2.rectangle(image, top_left, bottom_right,(0,0,255),2)
                    cv2.putText(image, match, (face_location[3], face_location[2]+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    def get_frame(self,frame):
        if frame.shape:
            self.face_recog(frame)

face_r = FaceRecog()
            
@app.route("/", methods=["POST"])
def home():
    img = request.form.get("image")
    jpg_original = base64.b64decode(img)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    image_buffer = cv2.imdecode(jpg_as_np, flags=1)
    st = time.time()
    face_r.get_frame(image_buffer)
    en = time.time()
    print(en - st)
    return 'Success!'

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True,port="7000",threaded=True)