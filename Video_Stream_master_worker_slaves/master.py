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
import pickle
import face_recognition
import os

########################################################################################################################################################
# assign and keep workers or nodes

workers = [[0,"http://127.0.0.1:5000"],[0,"http://127.0.0.1:5001"]]
nodes_dict = {
    "face_recog": [[0,"http://127.0.0.1:6000/"],[0,"http://127.0.0.1:6001/"]],
    "mask_recog": [[0,"http://127.0.0.1:6002/"]]
}

def assignner(lst,listOf):
    if len(lst) == 0:
        print("[master][ping_to_cloud][assignner] No {} available for assignment please provide {}".format(listof,listOf))

    lst  = sorted(lst,key=lambda x:x[0])
    lst[0][0] = lst[0][0] + 1
    print("[master][ping_to_cloud][assignner]",listOf,":",lst)
    return lst[0][1],lst


def unassignner(cam,lst,listOf):
    ll = -1
    for i in range(len(lst)):
        if lst[i][1] == cam:
            ll = i
            break
    if ll == -1:
        print("[master][ping_to_cloud][unassignner] May camera not assign to any {}".format(listOf))
    else:
        lst[ll][0] -= 1
        if lst[ll][0] < 0:
            lst[ll][0] = 0
    print("[master][ping_to_cloud][unassignner] ",listOf,":",cam,lst)
    return lst
    
    
    
########################################################################################################################################################### 





onlineDB = "http://127.0.0.1:7000/onlinedb"
cloudFun = "http://127.0.0.1:7000/cloudfun"

# ip_cam2 = "http://192.168.252.2:8080/video"
# ip_cam = 0
# # x = requests.post(url, data = {"ip_cam":ip_cam1})
# a = requests.post(workers[0]+"/startworker", json = {"ip_cam":ip_cam,"services":["face_recog"]})
# b = requests.post(workers[1]+"/startworker", json = {"ip_cam":ip_cam2,"services":["face_recog","mask_recog"]})

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
            print("[master][sync_database_online] Data is sent for sycning online Database with local database")
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
            print("[master][sync_database_online]",e)
            print("[master][sync_database_online] Not able to update online database, may be system not connect to internet or any other issue in sync_database_online function")
            print("-"*40)
        finally:
            time.sleep(60)
            
########################################################################################################################

def ping_to_cloud(url):
    global workers,nodes_dict
    while True:
        try:
            print("-"*40)
            
            print("[master][ping_to_cloud] Retreving data from cloud function")
            res = requests.get(url)
            ip_configs = res.json()
            allIpsOnline = []
            
            for ip_config in ip_configs:
                if ip_config:
                    ip_cam_db = IpConfig.query.filter(IpConfig.camera_ip == ip_config["ip_cam"]).all()
                    
                    # Create new ipcamera 
                    if len(ip_cam_db)==0:
                        
                        #############################################################################################
                        # worker assign and node assign
                        worker,workers = assignner(workers,"worker")
                    
                        ip_config_new = ip_config.copy()
                        nodesForServices = []
                        for serv in ip_config["services"]:
                            node,nodes_dict[serv] = assignner(nodes_dict[serv],"node")
                            nodesForServices.append(node)
                        new = {"nodes":nodesForServices}
                        ip_config_new.update(new)
                        
                        ###############################################################################################
                        # save in database
                        
                        newip = IpConfig(camera_ip=str(ip_config["ip_cam"]),services=ip_config["services"],worker=worker,nodes=nodesForServices)
                        db_session.add(newip)
                        db_session.commit() 
                        
                        ###############################################################################################
                        # request to create worker
                        
                        requests.post(worker +"/startworker", json = ip_config_new)
                        print("[master][ping_to_cloud] ip config:",ip_config_new,"assigned to worker:",worker)
                        
                        ################################################################################################
                    
                     # Update ipcamera 
                    elif len(ip_cam_db)==1:
                        
                        ip_cam_db_first = ip_cam_db[0]
                        if ip_config["services"] != ip_cam_db_first.services:
                            
                        ################################################################################################
                        # unassign nodes,worker and stop camera
                        
                            workers = unassignner(ip_cam_db_first.worker,workers,"worker")
                            for serv,nd in zip(ip_cam_db_first.services,ip_cam_db_first.nodes):
                                nodes_dict[serv] = unassignner(nd,nodes_dict[serv],"nodes")
                            worker = ip_cam_db_first.worker
                            requests.post(worker +"/stopworker", json = ip_config)
                            
                        ##################################################################################################
                        # worker assign and node assign
                        
                            worker,workers = assignner(workers,"worker")
                            ip_config_new = ip_config.copy()
                            nodesForServices = []
                            for serv in ip_config["services"]:
                                node,nodes_dict[serv] = assignner(nodes_dict[serv],"node")
                                nodesForServices.append(node)
                            new = {"nodes":nodesForServices}
                            ip_config_new.update(new)
                            
                        ####################################################################################################
                        # save in database
                            ip_cam_db_first.services = ip_config["services"]
                            ip_cam_db_first.nodes = nodesForServices
                            ip_cam_db_first.worker = worker 
                            db_session.commit()
                            
                        ####################################################################################################
                        # request to create new worker
                        
                            requests.post(worker +"/startworker", json = ip_config_new)
                            print("[master][ping_to_cloud] Any service is updated in camera:",ip_cam_db_first)
                        ####################################################################################################
                        
                    else: 
                        print("[master][ping_to_cloud] May be two or more same ip in ipconfig table(database), Please remove same ip if present")
                        
                    allIpsOnline.append(str(ip_config["ip_cam"]))
                        
            # Delete ipcamera
            allIpsLocal = IpConfig.query.all()
            for ip_camera in allIpsLocal:
                if ip_camera.camera_ip not in allIpsOnline:
                    json_data = {"ip_cam":ip_camera.camera_ip,"services":ip_camera.services}
                    requests.post(ip_camera.worker +"/stopworker", json = json_data)
                    print("[master][ping_to_cloud]",ip_camera.camera_ip,"ip camera stopped and deleted")
                    db_session.delete(ip_camera)
                    db_session.commit()
                    print("[master][ping_to_cloud]",ip_camera.camera_ip,"ip camera deleted from local database")
                    workers = unassignner(ip_camera.worker,workers,"worker") 
                    for serv,nd in zip(ip_camera.services,ip_camera.nodes):
                        nodes_dict[serv] = unassignner(nd,nodes_dict[serv],"nodes")
                    
            print("-"*40)
        except Exception as e:
            print("-"*40)
            print(e)
            print("[master][ping_to_cloud] Not able to update online database, may be system not connect to internet or any other issue in ping_to_cloud function")
            print("-"*40)
        finally:
            time.sleep(20)
            
########################################################################################################################3
# Face recognition encoding loading and update

face_cascade = cv2.CascadeClassifier(os.getcwd() + '/haarcascade_frontalface_default.xml')

def update_encoding():
    global known_names,known_faces,face_cascade
    known_names=[]
    known_faces=[]
    print("[master][update_encoding] Loading Encoding")
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
    with open("encoding.txt","wb") as file:
        pickle.dump({"known_encoding":known_faces,"known_name":known_names},file)
        
update_encoding()

########################################################################################################################3
#Starting workers and nodes present in local database

allIpsLocal = IpConfig.query.all()
print("[master] Starting workers and nodes present in local database!!")
for ip_camera in allIpsLocal:
    worker,workers = assignner(workers,"worker")
    ip_config_new = {"ip_cam":ip_camera.camera_ip,"services":ip_camera.services}
    nodesForServices = []
    for serv in ip_camera.services:
        node,nodes_dict[serv] = assignner(nodes_dict[serv],"node")
        nodesForServices.append(node)
    new = {"nodes":nodesForServices}
    ip_config_new.update(new)
    
    ip_camera.nodes = nodesForServices
    ip_camera.worker = worker 
    db_session.commit()
    
    requests.post(worker +"/startworker", json = ip_config_new)
    print("[master][ping_to_cloud] ip config:",ip_config_new,"assigned to worker:",worker)


########################################################################################################################
# Starting threads for syncing

t1 = threading.Thread(target=sync_database_online,args=[onlineDB])
print("[master] Starting syncing of local database to online database!!")
t1.start()    
t2 = threading.Thread(target=ping_to_cloud,args=[cloudFun])
print("[master] Starting syncing of online database to local database!!")
t2.start()    

########################################################################################################################3

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
    print("[master][index]",camera_name,face,timestamp,service)
    return "Local database is updated"

@app.route('/deleteallcamerainfo')
def deleteAllCameraInfo():
    logs = CameraInfo.query.all()
    print("[master][deleteAllCameraInfo] Deleting All CameraInfo")
    for l in logs:
        db_session.delete(l)
    db_session.commit()
    return "All records of camera info deleted succesfully"

@app.route('/deleteallipconfig')
def deleteAllIpConfig():
    print("[master][deleteAllIpConfig] Deleting All IpConfig")
    logs = IpConfig.query.all()
    for l in logs:
        db_session.delete(l)
    db_session.commit()
    return "All records of ip config deleted succesfully"

@app.route('/updateencoding')
def retrian():
    update_encoding()
    for face_recog_node in nodes_dict["face_recog"]:
        print(face_recog_node)
        requests.get(face_recog_node[1]+"/retrain")
    return "Update encoding succeful"

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



if __name__ == "__main__":
    app.run(host="127.0.0.1",debug=False,port=7001,threaded=True)
    