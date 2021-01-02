import base64
import numpy as np
from flask import Flask, render_template, Response, jsonify,request
from imutils.video import VideoStream
import cv2
import threading
import time
import os
import face_recognition
app = Flask(__name__)



@app.route('/')
def index():
    return "hello"

load_encodings = False
face_cascade = cv2.CascadeClassifier(os.getcwd() + '/haarcascade_frontalface_default.xml')
known_names,known_faces = [],[]
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

    def __del__(self):
        self.video.stream.release() 	

    def stop(self):
        self.video.stream.release()



    def face_detection(self,image):
        rects = []
        self.face_cascade = cv2.CascadeClassifier(os.getcwd() + '/haarcascade_frontalface_default.xml')
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
                        print(f"Match Found:", {match}," in camera ",str(self.url))
                    else:
                        match = "Unknown found in camera " + str(self.url)
            

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
        st = time.time()
        if self.frame.shape:
            self.face_recog()
        ret, jpeg = cv2.imencode('.jpg', self.frame)
        en = time.time()
        print(en - st)
        return jpeg.tobytes()



# @app.route('/video_feed')
# def video_feed():
#     if request.method == "post":
#         url = request.form.get("ip_cam")
#         print(url)
#     else:
#         url = 0

# light_on = False
# camera = None
camera_obj_dis = {}

# @app.before_first_request
def light_thread(camera):
    print(camera)
    while camera[0]:
        frame = camera[1].get_frame()


@app.route('/start',methods=['GET', 'POST'])
def start():
    # stop the function test
    global camera_obj_dis
    if request.method == "POST":
        url = request.form.get("ip_cam")
        print("post-->",url)
        if url == "0":
            url = 0
        flag = True
        if url in camera_obj_dis:
            if camera_obj_dis[url][0]:
                flag = False
        if flag:
            camera_obj_dis[url] = [False,VideoCamera(url)]
            thread = threading.Thread(target=light_thread,args=[camera_obj_dis[url]])
            camera_obj_dis[url][0] = True
            thread.start()
            
    return "started"

@app.route('/stop',methods=['GET', 'POST'])
def stop():
    global camera_obj_dis
    if request.method == "POST":
        url = request.form.get("ip_cam")
        if url == "0":
            url = 0
        if url in camera_obj_dis:
            if camera_obj_dis[url][0]:
                camera_obj_dis[url][1].stop()
                print("camera :",url," Stopped")
                camera_obj_dis[url][0] = False
        else:
            print("camera: {} you trying to stop is not in camera_obj_dis".format(url))
            
        
    return 'stopped'


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True,port="5000",threaded=True)
