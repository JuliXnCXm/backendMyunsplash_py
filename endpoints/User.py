import base64
from fastapi import APIRouter, status,Depends,Response,HTTPException
from fastapi.security import HTTPBasic
from services.BasicAuth import BasicAuth
from datetime import timedelta
from fastapi.encoders import jsonable_encoder
from services.AuthController import AuthController
from starlette.responses import RedirectResponse

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

router = APIRouter(
    tags=["User"],
    responses={404: {"description": "Not found"}},
)
security = HTTPBasic()
basic_auth = BasicAuth(auto_error=False)

@router.post(
    path="/login",
    tags=["User"],
    summary="Login",
    description="Login",
    response_description="Login",
    status_code=status.HTTP_201_CREATED)
def login(auth: BasicAuth = Depends(basic_auth)):
    if not auth:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response
    try:
        auth_handler = AuthController()
        decoded = base64.b64decode(auth).decode("ascii")
        email,_,password = decoded.partition(":")
        user = auth_handler.validate_user(email, password,False)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_handler.create_access_token(data={"sub":user["_id"]}, expires_delta=access_token_expires)
        token = jsonable_encoder(access_token)
        return token
    except Exception as e:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response

@router.post(
    path="/register",
    tags=["User"],
    summary="Register",
    description="Register a user",
    response_description="Register",
    status_code=status.HTTP_201_CREATED)
def register(auth: BasicAuth = Depends(basic_auth)):
    if not auth:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response
    try:
        auth_handler = AuthController()
        decoded = base64.b64decode(auth).decode("ascii")
        email,_,password = decoded.partition(":")
        user = auth_handler.validate_user(email, password, True)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password when creating user")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_handler.create_access_token(data={"sub":user["_id"]},expires_delta=access_token_expires)
        token = jsonable_encoder(access_token)

        return token
    except  Exception as e:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response

@router.get(
    path="/logout",
    tags=["User"],
    summary="Logout",
    description="Logout",
    response_description="Logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie("Authorization")
    return response
