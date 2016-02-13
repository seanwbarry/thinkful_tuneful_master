import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key = True)
    file = relationship("File", uselist=False, backref="song")
    
    def as_dictionary(self):
        """ return song data """
        song_data = {
            "id": self.id,
            "file": {
                "id": self.file.id,
                "name": self.file.filename
            }
        }
        return song_data
    
class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key = True)
    filename = Column(String(1024))
    song_id = Column(Integer, ForeignKey('songs.id'))
    
    def as_dictionary(self):
        file_data = {
            "id": self.id,
            "name": self.filename,
            "path": url_for("uploaded_file", filename=self.filename)
        }
        return file_data
        