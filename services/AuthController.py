import jwt
from connection import ConnDb
from config import config
from passlib.context import CryptContext
from datetime import datetime, timedelta
import re

class AuthController:

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.ALGORITHM = "HS256"

    def verifyPassword(self,password, password_hash):
        return self.pwd_context.verify(password, password_hash)

    def validate_user(self,email: str, password: str,isPostUser: bool):
        client = ConnDb.Connection()
        client.connect()
        collection = client.get_collection(config.config().DB_NAME,"users")
        if isPostUser and self.validateFields(email,password):
            try:
                if collection.count_documents({"email":email}) > 0:
                    return False
                userPosted = collection.insert_one({"email":email,"password": self.get_password_hash(password)})
                user = collection.find_one({"_id":userPosted.inserted_id})
                return user
            except Exception as e:
                print(e)
                return None
        else:
            user = collection.find_one({"email": email})
            if not self.verifyPassword(password, user["password"]):
                return False
        if not user:
            return False
        return user

    def validateFields(self,email,password):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            print("email")
            return False
        if not re.match(r"^[a-zA-Z0-9]{8,}$", password):
            print("password")
            return False
        return True

    def get_password_hash(self,password):
        re.match(r"",password)
        return self.pwd_context.hash(password)

    def create_access_token(self,*,data:dict, expires_delta=None):
        data_to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        data_to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(
            payload=data_to_encode,
            key=config.config().SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        return encode_jwt

    def decode_jwt(self,token):
        return jwt.decode(
            token,
            config.config().SECRET_KEY,
            algorithms=[self.ALGORITHM]
        )
