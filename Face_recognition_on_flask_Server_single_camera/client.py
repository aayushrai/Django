import requests
import cv2
import json

url = "http://127.0.0.1:7000/start"
ip_cam = "http://192.168.52.81:8080/video"
# ip_cam = 0
x = requests.post(url, data = {"ip_cam":ip_cam})
