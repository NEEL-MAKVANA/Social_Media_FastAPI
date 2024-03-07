from fastapi import APIRouter
from fastapi import HTTPException, status, Security
from database.db_config import SessionLocal
from src.models.user import User
from src.models.otp import Otp
from passlib.context import CryptContext
import smtplib
from datetime import datetime, timedelta
import random
from fastapi.security import OAuth2PasswordBearer
from src.schemas.user import (
    Print_user,
    Get_Users,
    Update_Users,
    All_Otp,
    Auth_schema,
    Final_Auth_schema,
    Reset_Pass_Email,
    New_Pass,
    Login_OTP,
    Login_Schema,
)
import uuid
from src.utils.utils_user_auth_token import (
    get_token,
    decode_token_user_email,
    decode_token_user_id,
)
from logs.log_config import logger

auth_router = APIRouter(tags=["User Auth Router"])
db = SessionLocal()

# --------- SMTP SERVER SETUP ------------#
# server = smtplib.SMTP("smtp.gmail.com", 587)
# server.starttls()
# server.login("makvananickfun@gmail.com", "reatchmqofwmjpfg")


# -------------------- CREATE A PASSLIB CONTEXT ----------------#
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------- CHECK WHETHER THE HASH PASSWORD AND USER ENTERED PASSWORD IS SAME OR NOT? -------------#
def pass_checker(user_pass, hash_pass):
    logger.info("Checking Password...")
    if pwd_context.verify(user_pass, hash_pass):
        logger.success("Password Matched")
        return True
    else:
        logger.error("Password is incorrect")
        raise HTTPException(status_code=401, detail="Password is incorrect")


# -------------------- GET ALL USER WHICH HAS IS_ACTIVE=TRUE AND IS_DELETED=FALSE AND IS_VERIFIED==TRUE --------------#
@auth_router.get("/", response_model=list[Print_user], status_code=status.HTTP_200_OK)
def get_all_user():
    logger.info("Retrieving items from database...")
    get_all = db.query(User).filter(
        (User.is_active == True)
        & (User.is_deleted == False)
        & (User.is_verified == True)
    )
    print(get_all)
    logger.info(f"Successfully retrievied item from database")
    logger.debug(get_all)
    return get_all


# -------------------------POST THE NEW USER ------------------------#


@auth_router.post("/add_user", response_model=Get_Users, status_code=status.HTTP_200_OK)
def add_user(user: Get_Users):
    logger.info("Finding user which has is_verified field set to true")
    find_user_is_verified_true = (
        db.query(User)
        .filter(
            ((User.uname == user.uname) & (User.email == user.email))
            & (User.is_verified == True)
        )
        .first()
    )
    logger.info("Finding user which has is_verified field set to false")

    find_user_is_verified_false = (
        db.query(User)
        .filter(
            ((User.uname == user.uname) & (User.email == user.email))
            & (User.is_verified == False)
        )
        .first()
    )

    if find_user_is_verified_true:
        logger.error("User found with is_verified true")

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="person already exist and already verified with this email and user name",
        )

    if find_user_is_verified_false:
        logger.error("User found with is_verified false")

        find_user_is_verified_false.is_active = True
        find_user_is_verified_false.is_deleted = False
        db.add(find_user_is_verified_false)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="person already exist but didn't verified yet !",
        )

    logger.info("Finding the user with current user name...")
    find_user_name = db.query(User).filter(User.uname == user.uname).first()

    if find_user_name:
        logger.error("User found with same user name")
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, detail="User name already taken"
        )
    logger.info("Finding the user with current user email id...")

    find_user_email = db.query(User).filter(User.email == user.email).first()

    if find_user_email:
        logger.error("User found with same user email id")

        raise HTTPException(
            status_code=status.HTTP_302_FOUND, detail="User email already taken"
        )

    logger.info("Adding new user....")
    newUser = User(
        id=str(uuid.uuid4()),
        fname=user.fname,
        lname=user.lname,
        uname=user.uname,
        email=user.email,
        password=pwd_context.hash(user.password),
    )
    db.add(newUser)
    db.commit()
    logger.success("User added successfully.")
    return newUser


# ------------------------ MODIFIED USER (GIVEN UNAME) --------------------------#


@auth_router.put(
    "/modify_user/{uname}",
    response_model=Get_Users,
    status_code=status.HTTP_200_OK,
)
def put_user(uname: str, user: Update_Users):
    logger.info("Finding User with same user name...")
    find_user = db.query(User).filter(User.uname == uname).first()

    logger.info("Checking whether the user is verified or not...")
    if find_user.is_verified == False:
        logger.error("User not verified yet.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not verified yet"
        )

    if not find_user:
        logger.error("User not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or User not verified yet",
        )
    logger.info("User field is updating...")
    hashed_password = pwd_context.hash(user.password)
    find_user.fname = user.fname
    find_user.lname = user.lname
    find_user.password = hashed_password
    pass_checker(user.password, hashed_password)
    db.add(find_user)
    db.commit()
    logger.success("User updated successfully.")
    return find_user


# ---------------------------- DELETE USER (GIVEN UNAME) ----------------------#


@auth_router.delete("/delete_user/{uname}")
def delete_user(uname: str):
    logger.info("User finding for deleting operation .....")
    find_user = db.query(User).filter(User.uname == uname).first()

    if find_user:
        logger.success("User found successfully.")
        find_user.is_active = False
        find_user.is_deleted = True
        find_user.is_verified = False
        db.add(find_user)
        db.commit()
        logger.success("User deleted successfully.")
    else:
        logger.error("User not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return "user deleted successfully"


# ------------------------------ GET ALL THE OTPS---------------------------#


@auth_router.get(
    "/get_allopts", response_model=list[All_Otp], status_code=status.HTTP_200_OK
)
def get_all_otp():
    logger.info("Getting opt from otp table...")
    all_otp = db.query(Otp).all()
    print(all_otp)
    if not all_otp:
        logger.error("Otp not found or Otp table empty")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="otp table is empty "
        )
    logger.success("Otp found successfully.")
    return all_otp


# ----------------------------------- GENERATE OTP ---------------------------------#


@auth_router.post("/generate_otp")
def authentication(auth_user: Auth_schema):
    logger.info("Finding user for generating otp....")
    find_user = db.query(User).filter((User.email == auth_user.email)).first()

    if not find_user:
        logger.error("User not found with this email id.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    logger.info("Otp generation....")
    random_number = random.randint(100000, 999999)
    print(random_number)
    logger.success(f"Otp generated successfylly and the otp is :{random_number}")
    newOtp = Otp(
        user_id=find_user.id,
        email=auth_user.email,
        otp=str(random_number),
    )
    print(f"\n\n ---------- OTP is ----------- {random_number} ------------\n\n")
    db.add(newOtp)
    db.commit()
    logger.success("Otp added successfully in table.")

    # # otp send to email
    # server.sendmail(
    #     "makvananickfun@gmail.com",
    #     auth_user.email,
    #     f"Your Otp is {random_number} which is valid for 1 minute",
    # )
    # print("mail sent")
    # server.quit()

    return "otp generated successful"


# ------------------------- OTP DELETE (FINAL AUTHENTICATION) -----------------------------


@auth_router.post("/final_authentication", status_code=status.HTTP_202_ACCEPTED)
def final_authentication(final_auth: Final_Auth_schema):
    logger.info("Finding user for verify otp....")

    find_user_from_usertable = (
        db.query(User).filter(User.email == final_auth.email).first()
    )

    logger.info("Fetching user email...")
    if not find_user_from_usertable:
        logger.error("User email not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )
    logger.success("User email fetch successfully.")

    logger.info("Finding user email with this otp...")
    find_user_acc_otp = (
        db.query(Otp)
        .filter((Otp.otp == final_auth.otp) & (Otp.email == final_auth.email))
        .first()
    )

    if not find_user_acc_otp:
        logger.error("User email not found with otp.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="otp and email not found"
        )

    prev_time = find_user_acc_otp.created_at
    curr_time = datetime.utcnow()
    logger.info("Checking the otp expire time.....")
    if (curr_time - prev_time) > timedelta(seconds=60):
        logger.warning("Otp expire need to try again.")
        db.delete(find_user_acc_otp)
        db.commit()
        return "Otp Expires"

    logger.success("User found with this email and otp.")
    find_user_from_usertable.is_verified = True
    find_user_from_usertable.is_active = True
    find_user_from_usertable.is_deleted = False

    db.delete(find_user_acc_otp)
    db.commit()

    logger.info("Generating token for further authentication....")
    access_token = get_token(
        find_user_from_usertable.id,
        find_user_from_usertable.email,
        find_user_from_usertable.uname,
    )
    logger.success(f"Token generated successfully and token is : {access_token}")
    return {"access_token": access_token}


# -------------------------ACCESS THE PROTECTED RESOURCE -----------------#

# OAuth2 scheme
oauth2_scheme_data_access = OAuth2PasswordBearer(tokenUrl="/final_authentication")


@auth_router.post("/protected_resource")
async def protected_resource(token: str = Security(oauth2_scheme_data_access)):
    logger.info("Decoding token information for accessing the data resource...")
    user_id = decode_token_user_id(token)
    logger.success("Decoded token information successfully.")
    logger.info("Fetching user id which is decoded through token in database...")
    user = db.query(User).filter(User.id == user_id, User.is_verified == True).first()

    if user.is_verified == False:
        logger.error("User not verified.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not verified yet"
        )
    if not user:
        logger.error("User not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    logger.success(
        f"User ID :{user.id} authenticated successfully and allow to access data"
    )
    return {"message": f"Congooo!! you have an access of very crucial data"}


# ---------------------------------RESET PASSWORD TOKEN GENERATION -------------------------------#


@auth_router.post(
    "/reset_password_token_generation", status_code=status.HTTP_202_ACCEPTED
)
def reset_pass_token_generation(entered_email: Reset_Pass_Email):
    logger.info("Fethching the user email id from database to reset password ....")
    find_email_user_table = (
        db.query(User)
        .filter(User.email == entered_email.email, User.is_verified == True)
        .first()
    )
    if find_email_user_table.is_verified == False:
        logger.error("User not verified with this email id.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not verified yet",
        )
    if not find_email_user_table:
        logger.error("User not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found",
        )
    logger.info("Generating token......")
    access_token = get_token(
        find_email_user_table.id,
        find_email_user_table.email,
        find_email_user_table.uname,
    )
    logger.success(f"Token generated successfully and the token is : {access_token}")
    return {"access_token": access_token}


# --------------------------------RESET PASSWORD -----------------------#
# OAuth2 scheme
oauth2_scheme_reset_pass = OAuth2PasswordBearer(
    tokenUrl="/reset_password_token_generation"
)


@auth_router.post("/reset_password", status_code=status.HTTP_202_ACCEPTED)
def reset_pass(new_pass: New_Pass, token: str = Security(oauth2_scheme_reset_pass)):
    logger.info("Decoding user email from token .....")
    user_email = decode_token_user_email(token)
    logger.success("Decoded successfully.")
    user = (
        db.query(User)
        .filter(User.email == user_email, User.is_verified == True)
        .first()
    )
    if user.is_verified == False:
        logger.error("User not verified.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not verified yet"
        )

    if not user:
        logger.error("User not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    logger.success("User found successfully and Addding the new password...")
    hashed_password = pwd_context.hash(new_pass.password)
    user.password = hashed_password
    db.add(user)
    db.commit()
    logger.success("User password changed successfully.")

    return {"message": f"Your password successfully changed"}


# -------------------------------LOGIN (OTP AND TOKEN GENERATION) -----------------------#
@auth_router.post("/login_otp_generation")
def login_otp_generation(login_field: Login_Schema):

    logger.info("Finding user data in database with same credentials...")
    find_user = (
        db.query(User)
        .filter(
            (User.uname == login_field.uname)
            & (
                (User.is_active == True)
                & (User.is_verified == True)
                & (User.is_deleted == False)
            )
        )
        .first()
    )

    if not find_user:
        logger.error("User not found or User not verified.")
        return "User not found or User not verified"

    if not pwd_context.verify(login_field.password, find_user.password):
        logger.error("Wrong password entered.")
        return "Wrong password entered"

    logger.info("Otp generation...")
    random_number = random.randint(100000, 999999)
    newOtp = Otp(
        user_id=find_user.id,
        email=find_user.email,
        otp=str(random_number),
    )
    logger.success(f"Otp generated successfully and the otp is : {random_number} ")
    print(f"\n\n ------ OTP is ------- {random_number} ----------\n\n")
    db.add(newOtp)
    db.commit()

    # server.sendmail(
    #     "makvananickfun@gmail.com",
    #     find_user.email,
    #     f"Your Otp is {random_number} which is valid for 1 minute",
    # )
    # print("mail sent")
    # server.quit()
    logger.info("Getting token....")
    access_token = get_token(find_user.id, find_user.email, find_user.uname)
    logger.success("Getting token successfully.")
    return {"access_token": access_token}


# --------------------------FINAL LOGIN USING TOKEN AND OTP---------------------#
# OAuth2 scheme
oauth2_login = OAuth2PasswordBearer(tokenUrl="/login_otp_generation")


@auth_router.post("/final_login_auth")
def final_login_auth(enter_otp: Login_OTP, token: str = Security(oauth2_login)):
    logger.info("Decoding token.....")
    user_email = decode_token_user_email(token)
    logger.success("Token decoded successfully.")

    # Fetch user data using email_id
    logger.info("Fetching data....")
    email_otp = (
        db.query(Otp)
        .filter((Otp.otp == enter_otp.otp) & (Otp.email == user_email))
        .first()
    )
    logger.success("Data fetch successfully")

    if not email_otp:
        logger.error("Otp Incorrect with this email id..")
        return "otp incorrect with this email id"

    prev_time = email_otp.created_at
    curr_time = datetime.utcnow()

    if (curr_time - prev_time) > timedelta(seconds=120):
        db.delete(email_otp)
        db.commit()
        logger.error("Otp Expires")
        return "Otp Expires"

    db.delete(email_otp)
    db.commit()
    logger.success(f"Successfully login")
    return {"message": f"You are Successfully login"}
