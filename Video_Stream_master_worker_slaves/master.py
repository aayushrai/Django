import requests
import cv2
import json
from flask import Flask,request
from database import db_session
from database import init_db
from models import CameraInfo,logger
import time
import threading
import datetime

url = "http://127.0.0.1:5000/start"
url2 = "http://127.0.0.1:5001/start"
ip_cam = "http://192.168.252.2:8080/video"
ip_cam1 = 0
onlineDB = "http://127.0.0.1:5010/"

# ip_cam2 = "http://192.168.52.190:8080/video"
# ip_cam = 0
# x = requests.post(url, data = {"ip_cam":ip_cam1})
a = requests.post(url, data = {"ip_cam":ip_cam,"service":"face_recog"})
b = requests.post(url2, data = {"ip_cam":ip_cam1,"service":"face_recog"})

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
                db_session.add(l)
                db_session.commit()
                
        except Exception as e:
            print("-"*40)
            print(e)
            print("Not able to update online database, may be system not connect to internet or any other issue in sync_database_online function")
            print("-"*40)
        finally:
            time.sleep(30)
            
            

t = threading.Thread(target=sync_database_online,args=[onlineDB])
t.start()    
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

@app.route('/deleteall')
def deleteAllRecod():
    logs = CameraInfo.query.all()
    for l in logs:
        db_session.delete(l)
    db_session.commit()
    return "All record deleted succesfully"

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



if __name__ == "__main__":
    app.run(host="127.0.0.1",debug=True,port=5050,threaded=True)