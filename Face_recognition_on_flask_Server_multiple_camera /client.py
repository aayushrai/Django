import requests
import cv2
import json

url = "http://127.0.0.1:5000/start"
ip_cam1 = "http://192.168.52.81:8080/video"
# ip_cam2 = "http://192.168.52.190:8080/video"
ip_cam = 0
x = requests.post(url, data = {"ip_cam":ip_cam1})
a = requests.post(url, data = {"ip_cam":ip_cam})
# b = requests.post(url, data = {"ip_cam":ip_cam2})