from datetime import date, datetime

from pydantic import BaseModel, Field
class Photo(BaseModel):
    photoname: str
    path: str
    photourl: str
    created: datetime = Field(default=datetime.now())
    user_id: str