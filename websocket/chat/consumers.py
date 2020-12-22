

import json
from channels.generic.websocket import WebsocketConsumer
import cv2
import base64

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)
        if message == "ok":
            # while True:
            img = cv2.imread("/home/uchiha/Desktop/websocket/chat/1.jpeg")
            
            # img2 = "data:image/jpeg;base64," + str(encodedImage)
            # (flag, encodedImage) = cv2.imencode(".jpg", img)
            # img2= b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'

            data = {}
            encodedImage = base64.b64encode(img)
            data['bytes'] = encodedImage
            self.send(text_data=json.dumps(data))

        

    # def generate():
    #     # grab global references to the output frame and lock variables
    #     global outputFrame, lock
    #     # loop over frames from the output stream
    #     while True:
    #         # wait until the lock is acquired
    #         with lock:
    #             # check if the output frame is available, otherwise skip
    #             # the iteration of the loop
    #             if outputFrame is None:
    #                 continue
    #             # encode the frame in JPEG format
    #             (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
    #             # ensure the frame was successfully encoded
    #             if not flag:
    #                 continue
    #         # yield the output frame in the byte format
    #         yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
    #             bytearray(encodedImage) + b'\r\n')
    

