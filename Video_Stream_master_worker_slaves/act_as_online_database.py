from flask import Flask,request,jsonify
import os
# print("virtual env: ",os.environ['VIRTUAL_ENV'])

app = Flask(__name__)


@app.route("/onlinedb",methods=["POST","GET"])
def onlineDB():
    print("Request in onlinedb")
    camera_name = request.form.get("camera")
    face = request.form.get("face")
    timestamp = request.form.get("timestamp")
    service = request.form.get("service")
    print(camera_name,face,timestamp,service)
    # print(request.form.get("logs"))
    return "connected"


ip_config = [{"ip_cam":0,"services":["face_recog","mask_recog"]},{"ip_cam":"http://192.168.43.173:8080/video","services":["face_recog","mask_recog"]}]

@app.route("/cloudfun",methods=["POST","GET"])
def cloudFun():
    print("Request in clouldfun")
    return jsonify(ip_config)

if __name__ == "__main__":
    app.run(host="127.0.0.1",debug=True,port=7000)