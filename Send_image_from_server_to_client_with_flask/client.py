import requests
import cv2
import base64
import json
img = cv2.imread("1.jpg")
retval, buffer = cv2.imencode('.jpg', img)

# Convert to base64 encoding and show start of data
jpg_as_text = base64.b64encode(buffer)

url = "http://127.0.0.1:5000/"
x = requests.post(url, data = {"image":jpg_as_text})