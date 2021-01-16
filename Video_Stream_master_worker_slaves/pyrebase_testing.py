import pyrebase

firebaseConfig = {  
    "apiKey": "AIzaSyBSDbmpwNb8NVim7FoLGV5F80NENCP5KVQ",
    "authDomain": "videostream-b5891.firebaseapp.com",
    "projectId": "videostream-b5891",
    "storageBucket": "videostream-b5891.appspot.com",
    "messagingSenderId": "877147488433",
    "appId": "1:877147488433:web:4b892516891c55c0f06290",
    "measurementId": "G-NHJSPKKG32",
    "databaseURL":"https://videostream-b5891-default-rtdb.firebaseio.com/"
    }

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

data = {"camera_ip":"192.338402.32.4","service_result":"aayush","timestamp":342432423,"services":["face_recog","mask_recog"]}

db.push(data)