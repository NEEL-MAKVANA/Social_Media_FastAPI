from pydantic import BaseModel
from typing import List, Dict
from typing import Any


class OurBasemodel(BaseModel):
    class Config:
        from_attributes = True


class AddStory(OurBasemodel):
    types:str

class GetStory(BaseModel):
    id:str
    user_id:str
    types:str
    likes:int
