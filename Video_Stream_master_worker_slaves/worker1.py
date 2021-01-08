import base64
import numpy as np
from flask import Flask, render_template, Response, jsonify,request
from imutils.video import VideoStream
import cv2
import threading
import time
import os
import requests
import datetime
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

nodes = ["http://127.0.0.1:6000/","http://127.0.0.1:7000/"]


def create_request_to_slave(url,jpg_as_text,camera_name,timeout,timestamp,service):
    try:
        requests.post(url, data = {"image":jpg_as_text,"camera":camera_name,"timestamp":timestamp,"service":service},timeout=timeout)
    except Exception as e:
        print("Request time out")
        print("Exception:",e)
        
# @app.before_first_request
def face_recog_thread(camera,camera_name,service):
    print(camera)
    global counter
    while camera[0]:
        frame = camera[1].get_frame()
        timestamp = datetime.datetime.now()
        if frame.shape:
            retval, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            create_request_to_slave(nodes[0],jpg_as_text,camera_name,1,timestamp,service)   


@app.route('/startworker',methods=['GET', 'POST'])
def start():
    # stop the function test
    global camera_obj_dis
    if request.method == "POST":
        ip_config = request.get_json()
        url = ip_config["ip_cam"]
        services = ip_config["services"]
        print("post-->",url)
        if url == "0":
            url = 0
        flag = True
        if url in camera_obj_dis:
            if camera_obj_dis[url][0]:
                print("Camera:{} is already running".format(url)," restarting camera.")
                camera_obj_dis[url][1].stop()
                camera_obj_dis[url][0] = False
                del camera_obj_dis[url]
        if flag:
            camera_obj_dis[url] = [False,VideoCamera(url)]
            for service in services:
                print("-"*50)
                if service == "face_recog":
                    thread = threading.Thread(target=face_recog_thread,args=[camera_obj_dis[url],url,service])
                    camera_obj_dis[url][0] = True
                    thread.start()
                    print("Face recongnition service is started")
                else:
                    print(service," service not available")
                print("-"*50)
                
    return "started"

@app.route('/stopworker',methods=['GET', 'POST'])
def stop():
    global camera_obj_dis
    if request.method == "POST":
        ip_config = request.get_json()
        url = ip_config["ip_cam"]
        services = ip_config["services"]
        if url == "0":
            url = 0
        if url in camera_obj_dis:
            camera_obj_dis[url][1].stop()
            camera_obj_dis[url][0] = False
            print("camera :",url," Stopped")
            del camera_obj_dis[url] 
        else:
            print("camera: {} you trying to stop is not in camera_obj_dis".format(url))
                  
    return 'stopped'


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True,port="5000",threaded=True)
