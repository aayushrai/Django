from flask import Flask, request
import cv2
import base64
import numpy as np
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/", methods=["POST"])
def home():
    img = request.form.get("image")
    jpg_original = base64.b64decode(img)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    image_buffer = cv2.imdecode(jpg_as_np, flags=1)
    print(image_buffer)
    cv2.imwrite("11.jpg",image_buffer)
    return 'Success!'

if __name__ == '__main__':
    app.run()
