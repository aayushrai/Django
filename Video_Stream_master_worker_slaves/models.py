from sqlalchemy import Column, Integer, String,TIMESTAMP
from database import Base

class CameraInfo(Base):
    __tablename__ = 'cameraInfo'
    id = Column(Integer, primary_key=True)
    camera_name = Column(String(200))
    face = Column(String(120))
    timestamp = Column(TIMESTAMP(timezone=False))
    service = Column(String(100))
    
    
    def __init__(self, camera_name=None, face=None,timestamp=None,service=None):
        self.camera_name = camera_name
        self.face = face
        self.timestamp = timestamp
        self.service = service


    def __repr__(self):
        return '<camera_name %r>' % (self.camera_name)

class logger(Base):
    __tablename__ = 'logger'
    id = Column(Integer, primary_key=True)
    lastupdate = Column(TIMESTAMP(timezone=False))

    
    def __init__(self, lastupdate):
        self.lastupdate = lastupdate


    def __repr__(self):
        return '<lastupdate %r>' % (str(self.lastupdate))
