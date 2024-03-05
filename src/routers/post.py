from fastapi import APIRouter
from fastapi import HTTPException, status, Security
from database.db_config import SessionLocal
from src.models.user import User
from src.models.post import Post
from src.models.follower_following import FollowerFollowing
from fastapi.security import OAuth2PasswordBearer
from src.schemas.post import ModifyPost, AddPost, CommentPost,GetPost
import uuid
from src.utils.utils_user_auth_token import decode_token_user_id



post_router = APIRouter(tags=["Post Router"])
db = SessionLocal()

# OAuth2 scheme
post_auth_scheme = OAuth2PasswordBearer(tokenUrl="/login_otp_generation")

#------------------GET ALL THE POST FROM THE TABLE-------------------#
@post_router.get("/getpost",response_model=list[GetPost],status_code=status.HTTP_200_OK)
def get_all_posts():
    all_post = db.query(Post).filter((Post.is_active==True) & (Post.is_deleted==False))
    if not all_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="POST TABLE EMPTY")
    return all_post


#------------------GET POST BY USER_ID------------------#
@post_router.get("/getpost/{user_id}",response_model=list[GetPost],status_code=status.HTTP_200_OK)
def get_all_posts(user_id:str):

    find_user=db.query(User).filter(User.id == user_id).first()
    if not find_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="USER NOT FOUND")
    all_post = db.query(Post).filter(Post.user_id==user_id).all()
    if not all_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="POST NOT FOUND WITH THIS PARTICULAR USER ID")

    return all_post

#-----------------GET POST OF MY FOLLOWING LIST--------------#

@post_router.get("/getpost_following_list",response_model=list[GetPost],status_code=status.HTTP_200_OK)
def get_all_posts(token: str = Security(post_auth_scheme)):
    token_user_id = decode_token_user_id(token)
    find_user=db.query(FollowerFollowing).filter(FollowerFollowing.user_id == token_user_id).first()
    if not find_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="USER NOT FOUND")

    token_following_list = find_user.following.copy()

    print(token_following_list)
    list_of_post=[]
    for id in token_following_list:
        all_post=db.query(Post).filter(Post.user_id == id).all()
        for post in all_post:
            list_of_post.append(post)

    return list_of_post



#----------------- ADD NEW POST -------------------------#


@post_router.post("/addpost", response_model=AddPost)
def add_post(addpost: AddPost, token: str = Security(post_auth_scheme)):
    token_user_id = decode_token_user_id(token)

    if not token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

    newPost = Post(
        id = str(uuid.uuid4()),
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

#------------------- MODIFY POST ----------------------------#
post_auth_scheme = OAuth2PasswordBearer(tokenUrl="/login_otp_generation")
@post_router.put("/modifypost/{post_id}")
def modify_post(post_id: str, modify_post: ModifyPost,token:str=Security(post_auth_scheme)):

    token_user_id = decode_token_user_id(token) #typically this line will check the token has expire or not
    # exp_time_check = db.query(User).filter(User.id == token_user_id).first()
    # if not exp_time_check:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Token expire or invalid token")

    find_post = db.query(Post).filter(Post.id == post_id).first()
    find_post.types = modify_post.types
    find_post.title = modify_post.title
    find_post.description = modify_post.description
    db.add(find_post)
    db.commit()
    return "post has been modified"





#------------------ DELETE POST -----------------------#

@post_router.delete("/deletepost/{post_id}")
def delete_post(post_id: str,token:str=Security(post_auth_scheme)):
    token_user_id = decode_token_user_id(token)#typically this line will check the token has expire or not
    # exp_time_check = db.query(User).filter(User.id == token_user_id).first()
    # if not exp_time_check:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Token expire or invalid token")
    find_post = db.query(Post).filter(Post.id == post_id).first()
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(find_post)
    db.commit()
    return "post deleted successfully"


#---------------------LIKE POST --------------------------------#
@post_router.put("/likepost/{post_id}")
def like_post(post_id: str,token:str=Security(post_auth_scheme)):
    token_user_id = decode_token_user_id(token)#typically this line will check the token has expire or not
    # exp_time_check = db.query(User).filter(User.id == token_user_id).first()
    # if not exp_time_check:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Token expire or invalid token")

    find_post = db.query(Post).filter(Post.id == post_id).first()
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    prev_likes = find_post.likes
    find_post.likes = prev_likes + 1
    db.add(find_post)
    db.commit()
    return "post has benn liked "


#------------------DISLIKE POST -------------------------#
@post_router.put("/dislikepost/{post_id}")
def dislike_post(post_id: str,token:str=Security(post_auth_scheme)):
    token_user_id = decode_token_user_id(token)#typically this line will check the token has expire or not
    # exp_time_check = db.query(User).filter(User.id == token_user_id).first()
    # if not exp_time_check:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Token expire or invalid token")

    find_post = db.query(Post).filter(Post.id == post_id).first()
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    prev_likes = find_post.likes
    if prev_likes==0:
        return "post has no likes yet so you can not dislike"
    find_post.likes = prev_likes - 1
    db.add(find_post)
    db.commit()
    return "post has benn disliked "


#---------------COMMENT ON POST -------------------#
@post_router.put("/commentpost/{post_id}")
def comment_post(
    post_id: str, cmt: CommentPost, token: str = Security(post_auth_scheme)
):
    token_user_id = decode_token_user_id(token)

    find_user = db.query(User).filter(User.id == token_user_id).first()
    user_name = find_user.uname
    find_post = db.query(Post).filter(Post.id == post_id).first()
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if find_post.comments:
        list_of_comments = find_post.comments.copy()
        list_of_comments.append({"user_name": user_name,"user_id":token_user_id, "comment": cmt.comment})
        find_post.comments = list_of_comments
        db.add(find_post)
        db.commit()

    else:
        list_of_comments = []
        list_of_comments.append({"user_name": user_name,"user_id":token_user_id, "comment": cmt.comment})
        find_post.comments = list_of_comments
        db.add(find_post)
        db.commit()
    return "comment added successfully"
