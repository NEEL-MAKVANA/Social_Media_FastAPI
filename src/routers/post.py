from fastapi import APIRouter
from fastapi import HTTPException, status, Security
from database.db_config import SessionLocal
from src.models.user import User
from src.models.post import Post
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from cofig import secret_key, algorithm
from src.schemas.post import ModifyPost, AddPost, CommentPost,GetPost


post_router = APIRouter(tags=["Post Router"])
db = SessionLocal()

#------------------get all the post-------------------#
@post_router.get("/getpost",response_model=list[GetPost],status_code=status.HTTP_200_OK)
def get_all_posts():
    all_post = db.query(Post).filter((Post.is_active==True) & (Post.is_deleted==False))
    return all_post


#------------------get post by user_id------------------#
@post_router.get("/getpost/{user_id}",response_model=list[GetPost],status_code=status.HTTP_200_OK)
def get_all_posts(user_id:str):
    find_user=db.query(User).filter(User.id == user_id).first()
    if not find_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
    all_post = db.query(Post).filter(Post.user_id==user_id).all()
    return all_post


#----------------- add new post -------------------------#
# OAuth2 scheme
post_auth_scheme = OAuth2PasswordBearer(tokenUrl="/login_otp_generation")

@post_router.post("/addpost", response_model=AddPost)
def add_post(addpost: AddPost, token: str = Security(post_auth_scheme)):

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        token_user_id = str(payload.get("user_id"))
        print(
            f"----------------------------------------{token_user_id}----------------------"
        )

        if not token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalid token"
        )

    newPost = Post(
        user_id=token_user_id,
        types=addpost.types,
        title=addpost.title,
        description=addpost.description,
        likes=0,
        comments=dict(),
    )

    db.add(newPost)
    db.commit()

    return newPost



#------------------- modify post ----------------------------#
@post_router.put("/modifypost/{post_id}")
def modify_post(post_id: str, modify_post: ModifyPost):
    find_post = db.query(Post).filter(Post.id == post_id).first()
    find_post.types = modify_post.types
    find_post.title = modify_post.title
    find_post.description = modify_post.description
    db.add(find_post)
    db.commit()
    return "post has been modified"
    pass



#-------------------------- delete post -----------------------#
@post_router.delete("/deletepost/{post_id}")
def delete_post(post_id: str):
    find_post = db.query(Post).filter(Post.id == post_id).first()
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(find_post)
    db.commit()
    return "post deleted successfully"
    pass



#---------------------like post --------------------------------#
@post_router.put("/likepost/{post_id}")
def like_post(post_id: str):
    find_post = db.query(Post).filter(Post.id == post_id).first()
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    prev_likes = find_post.likes
    find_post.likes = prev_likes + 1
    db.add(find_post)
    db.commit()
    return "post has benn liked "


#-------------------------dislike post -------------------------#
@post_router.put("/dislikepost/{post_id}")
def dislike_post(post_id: str):
    find_post = db.query(Post).filter(Post.id == post_id).first()
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    prev_likes = find_post.likes
    find_post.likes = prev_likes - 1
    db.add(find_post)
    db.commit()
    return "post has benn disliked "


#-------------------------------comment on post -------------------#
@post_router.put("/commentpost/{post_id}")
def comment_post(
    post_id: str, cmt: CommentPost, token: str = Security(post_auth_scheme)
):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        token_user_id = str(payload.get("user_id"))
        print(
            f"----------------------------------------{token_user_id}----------------------"
        )

        if not token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalid token"
        )
    find_user = db.query(User).filter(User.id == token_user_id).first()
    user_name = find_user.uname
    find_post = db.query(Post).filter(Post.id == post_id).first()
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if find_post.comments:
        list_of_comments = find_post.comments.copy()
        list_of_comments.append({"user_name": user_name, "comment": cmt.comment})
        find_post.comments = list_of_comments
        db.add(find_post)
        db.commit()

    else:
        list_of_comments = []
        list_of_comments.append({"user_name": user_name, "comment": cmt.comment})
        find_post.comments = list_of_comments
        db.add(find_post)
        db.commit()
    return "comment added successfully"
