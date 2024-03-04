from fastapi import APIRouter
from fastapi import  HTTPException, status, Security
from database.db_config import SessionLocal
from src.models.user import User
from src.models.follower_following import FollowerFollowing
from src.models.user import User
import smtplib
from fastapi.security import OAuth2PasswordBearer
from src.utils.utils_user_auth_token import decode_token_user_id


follower_following_router = APIRouter(tags=["Follower-Following Router"])
db = SessionLocal()


# ------------------------GET FOLLOWER OF PARTICULAR USER--------------------#

@follower_following_router.get("/getfollower/{path_user_id}")
def get_follower(path_user_id: str):
    find_user_in_table = (
        db.query(FollowerFollowing)
        .filter(FollowerFollowing.user_id == path_user_id)
        .first()
    )

    if not find_user_in_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    raw_follower_data = (
        find_user_in_table.follower
    )  # this will contain all the list of follower list

    uname_lst = []
    for id in raw_follower_data:
        find_data_in_user_table = db.query(User).filter(User.id == id).first()
        if not find_data_in_user_table:
            return "not user id not found"
        uname_lst.append(find_data_in_user_table.uname)

    return uname_lst
    # return find_user_in_table.follower


#---------------------------- GET FOLLOWING OF PARTICULAR USER---------------------#

@follower_following_router.get("/getfollowing/{path_user_id}")
def get_following(path_user_id: str):
    find_user_in_table = (
        db.query(FollowerFollowing)
        .filter(FollowerFollowing.user_id == path_user_id)
        .first()
    )

    if not find_user_in_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    raw_following_data = (
        find_user_in_table.following
    )  # this will contain all the list of follower list

    uname_lst = []
    for id in raw_following_data:
        find_data_in_user_table = db.query(User).filter(User.id == id).first()
        if not find_data_in_user_table:
            return "not user id not found"
        uname_lst.append(find_data_in_user_table.uname)

    return uname_lst
    # return find_user_in_table.following


# -------------------------------GET FOLLOWER COUNT OF PARTICULAR USER-------------------#

@follower_following_router.get("/getfollowercount/{path_user_id}")
def get_follower(path_user_id: str):
    find_user_in_table = (
        db.query(FollowerFollowing)
        .filter(FollowerFollowing.user_id == path_user_id)
        .first()
    )

    if not find_user_in_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    total_follower = len(find_user_in_table.follower)
    return total_follower


# -------------------------------GET FOLLOWING COUNT OF PARTICULAR USER ---------------------------#
@follower_following_router.get("/getfollowingcount/{path_user_id}")
def get_following(path_user_id: str):
    find_user_in_table = (
        db.query(FollowerFollowing)
        .filter(FollowerFollowing.user_id == path_user_id)
        .first()
    )

    if not find_user_in_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    total_following = len(find_user_in_table.following)
    return total_following



#--------------------------------FOLLOW REQUEST -----------------------------#
# OAuth2 scheme
follow_auth_scheme = OAuth2PasswordBearer(tokenUrl="/login_otp_generation")

@follower_following_router.put("/followrequest/{path_user_id}")
def follow_request(path_user_id: str, token: str = Security(follow_auth_scheme)):

    # find path_user_id in user table if that does not exist then we need to generate an exception
    find_path_user_in_user_tbl = db.query(User).filter(User.id == path_user_id).first()
    if not find_path_user_in_user_tbl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="path user id not found"
        )

    token_user_id = decode_token_user_id(token)

    if token_user_id == path_user_id:
            raise HTTPException(
                status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
                detail="token generated id path id both are same",
            )

    find_current_user_id_in_table = (
        db.query(FollowerFollowing)
        .filter(FollowerFollowing.user_id == token_user_id)
        .first()
    )

    find_path_user_id_in_table = (
        db.query(FollowerFollowing)
        .filter(FollowerFollowing.user_id == path_user_id)
        .first()
    )

    empty_follower = []
    empty_following = []

    if not find_current_user_id_in_table:
        print("--------------hello -----1----------")
        empty_following.append(path_user_id)
        current_user_entry = FollowerFollowing(
            user_id=token_user_id,
            follower=[],
            following=empty_following,
        )

        db.add(current_user_entry)
        db.commit()

    if not find_path_user_id_in_table:
        print("---------------hello -----2----------")
        empty_follower.append(token_user_id)
        path_user_entry = FollowerFollowing(
            user_id=path_user_id,
            follower=empty_follower,
            following=[],
        )
        db.add(path_user_entry)
        db.commit()

    if find_current_user_id_in_table:
        print("---------------hello -----3----------")
        curr_following = find_current_user_id_in_table.following.copy()

        if path_user_id in curr_following:
            return "User already in your following list"

        curr_following.append(path_user_id)
        find_current_user_id_in_table.following = curr_following
        db.add(find_current_user_id_in_table)
        db.commit()

    if find_path_user_id_in_table:
        print("---------------hello -----4----------")
        path_follower = find_path_user_id_in_table.follower.copy()

        if token_user_id in path_follower:
            return "User already in your follower list"

        path_follower.append(token_user_id)
        find_path_user_id_in_table.follower = path_follower
        db.add(find_path_user_id_in_table)
        db.commit()

    return "Follow Successfull"


#--------------------------------- UNFOLLOW USER------------------------------#

@follower_following_router.put("/unfollowrequest/{path_user_id}")
def unfollow_request(path_user_id: str, token: str = Security(follow_auth_scheme)):

    # find path_user_id in user table if that does not exist then we need to generate an exception
    find_path_user_in_user_tbl = db.query(User).filter(User.id == path_user_id).first()
    if not find_path_user_in_user_tbl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="path user id not found"
        )

    token_user_id = decode_token_user_id(token)

    if not token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

    if token_user_id == path_user_id:
            raise HTTPException(
                status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
                detail="token generated id path id both are same",
            )

    find_current_user_id_in_table = (
        db.query(FollowerFollowing)
        .filter(FollowerFollowing.user_id == token_user_id)
        .first()
    )

    find_path_user_id_in_table = (
        db.query(FollowerFollowing)
        .filter(FollowerFollowing.user_id == path_user_id)
        .first()
    )

    if find_path_user_id_in_table and find_current_user_id_in_table:
        print("-------------------- unfollow -------------------")
        take_following = find_current_user_id_in_table.following.copy()
        take_following.remove(path_user_id)
        find_current_user_id_in_table.following = take_following
        db.add(find_current_user_id_in_table)
        db.commit()

        take_follower = find_path_user_id_in_table.follower.copy()
        take_follower.remove(token_user_id)
        find_path_user_id_in_table.follower = take_follower
        db.add(find_path_user_id_in_table)
        db.commit()

        return "Unfollow Successfull"


# ------------------------------DELETE TABLE ENTRY FOR ADMIN SIDE ONLY ----------------------#

@follower_following_router.delete(
    "/deletefollowerfollowing/{id}", status_code=status.HTTP_202_ACCEPTED
)
def Delete(id: str):
    find_entity = db.query(FollowerFollowing).filter(FollowerFollowing.id == id).first()

    if not find_entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(find_entity)
    db.commit()
    return "Entry deleted successfully"
