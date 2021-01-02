from sqlalchemy import Column, Integer, String
from database import Base

class CameraInfo(Base):
    __tablename__ = 'cameraInfo'
    id = Column(Integer, primary_key=True)
    camera_name = Column(String(200))
    face = Column(String(120))
    timestamp = Column(String(50))
    
    def __init__(self, camera_name=None, face=None,timestamp=None):
        self.camera_name = camera_name
        self.face = face
        self.timestamp = timestamp


    def __repr__(self):
        return '<camera_name %r>' % (self.camera_name)
