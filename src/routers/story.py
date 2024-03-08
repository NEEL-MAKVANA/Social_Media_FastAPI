from fastapi import APIRouter
from fastapi import HTTPException, status, Security
from database.db_config import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from src.schemas.story import AddStory
from src.models.story import Story
from src.models.user import User
from datetime import datetime, timedelta
import uuid
from sqlalchemy import text
from src.schemas.story import GetStory
from src.utils.utils_user_auth_token import decode_token_user_id


story_router = APIRouter(tags=["Story Router"])
db = SessionLocal()


story_auth_scheme = OAuth2PasswordBearer(tokenUrl="/login_otp_generation")


# -------------------- GET STORY WITHIN 24 HOUR ------------------- #
@story_router.get("/getstory_timelimit/{user_id}", response_model=list[GetStory])
def get_story_within_time(user_id: str):

    find_user = db.query(User).filter(User.id == user_id).first()
    if not find_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    curr_time = datetime.utcnow()
    find_user_story_first = (
        db.query(Story)
        .filter(
            (Story.user_id == user_id)
            & (curr_time < (Story.created_at + timedelta(minutes=1)))
        )
        .first()
    )

    find_user_story = db.query(Story).filter(
        (Story.user_id == user_id)
        & (curr_time < (Story.created_at + timedelta(days=1)))
    )
    print(find_user_story)
    if not find_user_story_first:
        db.query(Story).filter(Story.user_id == user_id).delete(
            synchronize_session=False
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story has been expired"
        )

    return find_user_story


# -------------------- ADD NEW STORY -----------------------------#
# OAuth2 scheme
@story_router.post("/addstory", response_model=AddStory)
def add_story(addstory: AddStory, token: str = Security(story_auth_scheme)):

    token_user_id = decode_token_user_id(token)

    if not token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )
    newStory = Story(
        id=str(uuid.uuid4()),
        user_id=token_user_id,
        types=addstory.types,
        likes=0,
    )
    # insert_query = f"insert into stories values({str(uuid.uuid4())},{token_user_id},{addstory.types},{0})"
    # query = text(insert_query)
    # db.execute(query)
    db.add(newStory)
    db.commit()

    return newStory


# ---------------------- LIKE STORY  ------------------#
@story_router.post("/likestory/{story_id}")
def get_all_like(story_id: str, token: str = Security(story_auth_scheme)):
    token_user_id = decode_token_user_id(
        token
    )  # typically this line will check the token has expire or not

    find_story = db.query(Story).filter(Story.id == story_id).first()
    if not find_story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    find_story.likes = find_story.likes + 1
    db.commit()
    return "story liked successfully"


# ---------------------- DISLIKE STORY  ------------------#
@story_router.post("/dislikestory/{story_id}")
def get_all_likes(story_id: str, token: str = Security(story_auth_scheme)):
    token_user_id = decode_token_user_id(
        token
    )  # typically this line will check the token has expire or not
    find_story = db.query(Story).filter(Story.id == story_id).first()
    if not find_story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if find_story.likes == 0:
        return "you can't dislike because this has no likes yet"
    find_story.likes = find_story.likes - 1
    db.commit()
    return "story disliked successfully"


# --------------------- DELETE STORY ------------------------------#
@story_router.delete("/deletestory/{story_id}")
def delete_story(story_id: str, token: str = Security(story_auth_scheme)):
    token_user_id = decode_token_user_id(
        token
    )  # typically this line will check the token has expire or not
    find_story = db.query(Story).filter(Story.id == story_id).first()
    if not find_story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(find_story)
    db.commit()
    return "story deleted successfully"
