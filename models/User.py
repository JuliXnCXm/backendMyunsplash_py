from datetime import date, datetime
import bcrypt
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    lastname: str
    email: str
    password: str
    created: datetime = Field(default=datetime.now())
