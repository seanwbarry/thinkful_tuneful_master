import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path

file_schema = {
    "type": "object",
    "properties": {
        "file": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                }
            }
        }
    },
    "required": ["file"]
}

update_schema = {
    "type": "object",
    "properties": {
        "filename": {
            "type": "string"
        }
    }
}

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get a list of songs """
    songs = session.query(models.Song)
    songs = songs.order_by(models.Song.id)
    
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
def add_song():
    """ add a song from a file that exists """
    data = request.json
    
    try:
        validate(data, file_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    
    #add the song to the database
    id = data["file"]["id"]
    
    file_exists = session.query(models.File).get(id)
    
    if file_exists is None:
        data = {"message": "nopenopenope"}
        return Response(json.dumps(data), 422, mimetype="application/json")
    
    song = models.Song()
    song.file = file_exists
    session.add(song)
    session.commit()
    data = json.dumps(song.as_dictionary())
    return Response(data, 201, mimetype="application/json")
    
@app.route("/api/songs", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def edit_song():
    data = request.json
    
    try:
        validate(data, update_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    
    filename = data["filename"]
    id = data["id"]

    file_to_edit = session.query(models.File).get(id)
    
    if file_to_edit is None:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")        

    file_to_edit.filename = filename
    
    session.commit()
    
    data = json.dumps(file_to_edit.as_dictionary())
    return Response(data, 201, mimetype="application/json")

@app.route("/api/songs", methods=["DELETE"])
@decorators.accept("application/json")
@decorators.require("application/json")
def delete_song():
    data = request.json
    
    try:
        validate(data, file_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 404, mimetype="application/json")
        
    id = data["file"]["id"]    
        
    song_to_delete = session.query(models.Song).get(id)
    
    if not song_to_delete:
        message = "Could not find song the relevant song to delete"
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
        
    session.delete(song_to_delete)
    session.commit()
    
    message = "Song has been deleted!"
    data = json.dumps({"message": message})
    return Response(data ,200, mimetype="application/json")

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)
    
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    #why doesn't this have to be 'name' <--???
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))
    
    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")