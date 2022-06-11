from fastapi import APIRouter, Body,status,UploadFile,File,Request,HTTPException
from fastapi.responses import FileResponse
import shutil
from models.Photo import Photo
from connection import ConnDb
from config import config
from services.AuthController import AuthController
import os
from bson.json_util import dumps
from bson.objectid import ObjectId
from typing import List


router = APIRouter(
    tags=["Photos"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    path="/get_photo/{photo_id}",
    summary="Get photo",
    description="Get photo",
    )
def get_image(photo_id: str):
    try:
        client = ConnDb.Connection()
        client.connect()
        collection = client.get_collection(config.config().DB_NAME,"photos")
        image = collection.find_one({"_id": ObjectId(photo_id)})
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        path = os.path.dirname("storage/imgs/")

        return FileResponse(os.path.join(path, image["photoname"]))
    except Exception as e:
        print(e)

@router.get(
    path="/photos",
    summary="Get photos",
    description="Get photos",
    response_description="Get All photos",
    response_model=List[Photo],
    status_code=status.HTTP_200_OK,
    )
def retrieve_photos():
    client = ConnDb.Connection()
    client.connect()
    collection = client.get_collection(config.config().DB_NAME,"photos")
    photos = collection.find({})
    all_photos = dumps(list(photos))
    return all_photos

@router.post(
    path="/uploadphoto/{photoname}",
    tags=["Photos"],
    summary="Upload Photos",
    description="Upload Photos",
    response_description="Upload Photos",
    status_code=status.HTTP_201_CREATED)
def postphotos(
    photoname:str ,
    req : Request ,
    image: UploadFile = File(...)):

    try:
        client = ConnDb.Connection()
        client.connect()
        collection = client.get_collection(config.config().DB_NAME,"photos")
        authHandler = AuthController()
        path = ""
        photourl = ""
        if not image:
            photourl = req.body["fileForm"]
            path = photourl
        else:
            photourl = f"{config.config().API_URL}{image.filename}"
            path = f"storage/imgs/{image.filename}"

        #shutill process for handle files
        with open(path, 'wb') as buffer:
            shutil.copyfileobj(image.file, buffer)
            photo = Photo(
                photoname=photoname,
                path=path,
                photourl=photourl,
                user_id=authHandler.decode_jwt(req.cookies.get("Authorization"))
            )
        buffer.close()
        insertion = collection.insert_one(photo.dict()).inserted_id
    except Exception as e:
        print(e)

    return {
        "message": "Photo uploaded successfully",
        "status": "success",
        "data": {
            "id": str(insertion),
        }
    }

@router.delete(
    path="/deletephoto/{id}",
    tags=["Photos"],
    summary="Delete Photo",
    description="Delete Photo",
    response_description="Delete Photo",
    status_code=status.HTTP_200_OK)
def deletePhoto(id:str,req:Request):
    client = ConnDb.Connection()
    client.connect()
    collection = client.get_collection(config.config().DB_NAME,"photos")
    authHandler = AuthController()
    photo_data = collection.find_one({"_id": id})
    user_id = authHandler.decode_jwt(req.cookies.get("Authorization"))

    if user_id == photo_data["user_id"]:
        try:
            collection.delete_one({"_id": id})
            if os.path.exists(photo_data["path"]):
                os.remove(photo_data["path"])
        except Exception as e:
            print(e)

    return {
        "message": "Photo deleted successfully",
        "status": "success",
        "data": {
            "id": str(id),
        }
    }