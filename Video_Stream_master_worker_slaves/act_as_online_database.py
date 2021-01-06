from flask import Flask,request
app = Flask(__name__)

@app.route("/",methods=["POST","GET"])
def onlineDB():
    print("Request")
    camera_name = request.form.get("camera")
    face = request.form.get("face")
    timestamp = request.form.get("timestamp")
    service = request.form.get("service")
    print(camera_name,face,timestamp,service)
    # print(request.form.get("logs"))
    return "connected"



if __name__ == "__main__":
    app.run(host="127.0.0.1",debug=True,port=5010)