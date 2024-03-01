from pydantic import BaseModel


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
