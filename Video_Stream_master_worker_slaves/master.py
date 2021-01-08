import requests
import cv2
import json
from flask import Flask,request
from database import db_session
from database import init_db
from models import CameraInfo,logger,IpConfig
import time
import threading
import datetime

workers = ["http://127.0.0.1:5000","http://127.0.0.1:5001"]


onlineDB = "http://127.0.0.1:5010/onlinedb"
cloudFun = "http://127.0.0.1:5010/cloudfun"

ip_cam2 = "http://192.168.252.2:8080/video"
ip_cam = 0
# x = requests.post(url, data = {"ip_cam":ip_cam1})
a = requests.post(workers[0]+"/startworker", json = {"ip_cam":ip_cam,"services":["face_recog"]})
b = requests.post(workers[1]+"/startworker", json = {"ip_cam":ip_cam2,"services":["face_recog","mask_recog"]})

app = Flask(__name__)
init_db()



def sync_database_online(url):
    while True:
        lastupdateall = logger.query.all()
        if len(lastupdateall):
            lastupdate = lastupdateall[0].lastupdate
        else:
            lastupdate = None
        try:
            
            if not lastupdate:
                logs = CameraInfo.query.all()
            else:
                logs = CameraInfo.query.filter(CameraInfo.timestamp >= lastupdate).all()
    
            for obj in logs:
                data = {"face":obj.face,"camera":obj.camera_name,"timestamp":obj.timestamp,"service":obj.service}
                requests.post(url,data=data)
            
            print("-"*40)
            print("Data is sent for sycning online Database to local database")
            print("-"*40)
            
            newTime = datetime.datetime.now()

            if not lastupdate:
                l = logger(lastupdate=newTime)
                db_session.add(l)
                db_session.commit()
            else:
                l = logger.query.all()[0]
                l.lastupdate = newTime
                db_session.commit()
                
        except Exception as e:
            print("-"*40)
            print(e)
            print("Not able to update online database, may be system not connect to internet or any other issue in sync_database_online function")
            print("-"*40)
        finally:
            time.sleep(60)

def ping_to_cloud(url):
    global workers
    while True:
        try:
            print("-"*40)
            print("Retreving data from cloud function")
            res = requests.get(url)
            ip_configs = res.json()
            for ip_config in ip_configs:
                if ip_config:
                    ip_cam_db = IpConfig.query.filter(IpConfig.camera_ip == ip_config["ip_cam"]).all()
                    if len(ip_cam_db)==0:
                        newip = IpConfig(camera_ip=ip_config["ip_cam"],services=ip_config["services"])
                        db_session.add(newip)
                        db_session.commit()
                        print("ip config:",ip_config,"assigned to worker:",workers[0])
                    elif len(ip_cam_db)==1:
                        ip_cam_db_first = ip_cam_db[0]
                        if ip_config["services"] != ip_cam_db_first.services:
                            ip_cam_db_first.services = ip_config["services"]
                            db_session.commit()
                            requests.post(workers[0]+"/stopworker", json = ip_config)
                            requests.post(workers[0]+"/startworker", json = ip_config)
                            print("IpConfig updated for camera:",ip_cam_db_first)
                    else:
                        print("two or more same ip in ipconfig table")
                        
                        
                        
                    
                    # 
            print("-"*40)
         
            # if not lastupdate:
            #     l = logger(lastupdate=newTime)
            #     db_session.add(l)
            #     db_session.commit()
            # else:
            #     l = logger.query.all()[0]
            #     l.lastupdate = newTime
            #     db_session.add(l)
            #     db_session.commit()
                
        except Exception as e:
            print("-"*40)
            print(e)
            print("Not able to update online database, may be system not connect to internet or any other issue in ping_to_cloud function")
            print("-"*40)
        finally:
            time.sleep(10)
            
            

t1 = threading.Thread(target=sync_database_online,args=[onlineDB])
t1.start()    
t2 = threading.Thread(target=ping_to_cloud,args=[cloudFun])
t2.start()    
previous_recognised_face = ""
@app.route('/data', methods=["POST"])
def index():
    global onlineDB
    camera_name = request.form.get("camera")
    face = request.form.get("face")
    timestamp = request.form.get("timestamp")
    timestamp = datetime.datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S.%f")
    service = request.form.get("service")
    c = CameraInfo(camera_name=camera_name,face=face,timestamp=timestamp,service=service)
    db_session.add(c)
    db_session.commit()
    print(camera_name,face,timestamp,service)
    return "Local database is updated"

@app.route('/deleteallcamerainfo')
def deleteAllCameraInfo():
    logs = CameraInfo.query.all()
    print("Deleting All CameraInfo")
    for l in logs:
        db_session.delete(l)
    db_session.commit()
    return "All records of camera info deleted succesfully"

@app.route('/deleteallipconfig')
def deleteAllIpConfig():
    print("Deleting All IpConfig")
    logs = IpConfig.query.all()
    for l in logs:
        db_session.delete(l)
    db_session.commit()
    return "All records of ip config deleted succesfully"

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



if __name__ == "__main__":
    app.run(host="127.0.0.1",debug=True,port=5050,threaded=True)
    