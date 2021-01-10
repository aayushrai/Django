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


def create_request_to_slave(url,jpg_as_text,camera_name,timeout,timestamp,service):
    try:  
        requests.post(url, data = {"image":jpg_as_text,"camera":camera_name,"timestamp":timestamp,"service":service},timeout=timeout)
    except Exception as e:
        # print("-"*50)
        # print("Request time out")
        # print("Exception:",e)
        # print("-"*50)
        pass
        
# @app.before_first_request
def get_frame_and_send_it_to_slave(camera,camera_name,services,node_service):
    print(camera)
    while camera[0]:
        frame = camera[1].get_frame()
        timestamp = datetime.datetime.now()
        try:
            if len(frame):
                retval, buffer = cv2.imencode('.jpg', frame)
                jpg_as_text = base64.b64encode(buffer) 
                for index,service in enumerate(services):
                    create_request_to_slave(node_service[index],jpg_as_text,camera_name,1,timestamp,service) 
                camera[2] = False
        except Exception as e:
            if not camera[2]:
                print("[worker][get_frame_and_send_it_to_slave] Error:",e)
                print("[worker][get_frame_and_send_it_to_slave] Camera: {} May be the camera you trying to reach is not available currently or may be ip_camera id is wrong or may be any other error check error above.".format(camera_name))
                camera[2] = True



@app.route('/startworker',methods=['GET', 'POST'])
def start():
    # stop the function test
    global camera_obj_dis
    if request.method == "POST":
        ip_config = request.get_json()
        url = ip_config["ip_cam"]
        services = ip_config["services"]
        node_service = ip_config["nodes"]
        print("[worker][start] Starting worker for camera:",url)
        if url == "0":
            url = 0
        flag = True
        if url in camera_obj_dis:
            if camera_obj_dis[url][0]:
                print("[worker][start]Camera:{} is already running".format(url)," restarting camera.")
                camera_obj_dis[url][1].stop()
                camera_obj_dis[url][0] = False
                del camera_obj_dis[url]
        if flag:
            camera_obj_dis[url] = [False,VideoCamera(url),False]
            thread = threading.Thread(target=get_frame_and_send_it_to_slave,args=[camera_obj_dis[url],url,services,node_service])
            camera_obj_dis[url][0] = True
            thread.start()
            
                
                
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
            print("[worker][stop] camera :",url," Stopped and deleted")
            del camera_obj_dis[url] 
        else:
            print("[worker][stop] camera: {} you trying to stop is not in camera_obj_dis".format(url))
                  
    return 'stopped'


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True,port="5000",threaded=True)
