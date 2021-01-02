import base64
import numpy as np
from flask import Flask, render_template, Response, jsonify,request
from imutils.video import VideoStream
import cv2
import threading
import time
import os
import requests
app = Flask(__name__)



class VideoCamera():

    def __init__(self,url):
        self.url = url
        self.video=VideoStream(src=self.url).start()

    def __del__(self):
        self.video.stream.release() 	

    def stop(self):
        self.video.stream.release()
   
    def get_frame(self):
        self.frame = self.video.read()
        return self.frame


camera_obj_dis = {}
counter = 0

url1 = "http://127.0.0.1:6000/"
url2 = "http://127.0.0.1:7000/"
# @app.before_first_request
def light_thread(camera,camera_name):
    print(camera)
    global counter
    while camera[0]:
        frame = camera[1].get_frame()
        if counter%2:
            if frame.shape:
                retval, buffer = cv2.imencode('.jpg', frame)
                jpg_as_text = base64.b64encode(buffer)
                try:
                    requests.post(url1, data = {"image":jpg_as_text,"camera":camera_name},timeout=.5)
                except Exception as e:
                    print("Request time out")
                    print("Exception:",e)
        else:
            if frame.shape:
                retval, buffer = cv2.imencode('.jpg', frame)
                jpg_as_text = base64.b64encode(buffer)
                try:
                    requests.post(url2, data = {"image":jpg_as_text,"camera":camera_name},timeout=.5)
                except Exception as e:
                    print("Request time out")
                    print("Exception:",e)
    
        counter += 1
        


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
            thread = threading.Thread(target=light_thread,args=[camera_obj_dis[url],url])
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