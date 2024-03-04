from pydantic import BaseModel
from typing import List, Dict
from typing import Any


class OurBasemodel(BaseModel):
    class Config:
        from_attributes = True


class AddPost(OurBasemodel):
    types: str
    title: str
    description: str


class ModifyPost(AddPost):
    pass


class CommentPost(BaseModel):
    comment: str

class GetPost(BaseModel):
    id:str
    user_id:str
    types:str
    title:str
    description:str
    likes:int
    comments:Any


