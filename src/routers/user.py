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
from src.utils.utils_user_auth_token import get_token,decode_token_user_email,decode_token_user_id

auth_router = APIRouter(tags=["User Auth Router"])
db = SessionLocal()

#--------- SMTP SERVER SETUP ------------#
# server = smtplib.SMTP("smtp.gmail.com", 587)
# server.starttls()
# server.login("makvananickfun@gmail.com", "reatchmqofwmjpfg")


# -------------------- CREATE A PASSLIB CONTEXT ----------------#
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#----------------- CHECK WHETHER THE HASH PASSWORD AND USER ENTERED PASSWORD IS SAME OR NOT? -------------#
def pass_checker(user_pass, hash_pass):
    if pwd_context.verify(user_pass, hash_pass):
        print("\n\n-------both password are same ----------\n\n")
        return True
    else:
        raise HTTPException(status_code=401, detail="Password is incorrect")


#-------------------- GET ALL USER WHICH HAS IS_ACTIVE=TRUE AND IS_DELETED=FALSE AND IS_VERIFIED==TRUE --------------#
@auth_router.get("/", response_model=list[Print_user], status_code=status.HTTP_200_OK)
def get_all_user():
    get_all = db.query(User).filter(
        (User.is_active == True)
        & (User.is_deleted == False)
        & (User.is_verified == True)
    )
    print(get_all)
    return get_all


# -------------------------POST THE NEW USER ------------------------#

@auth_router.post("/add_user", response_model=Get_Users, status_code=status.HTTP_200_OK)
def add_user(user: Get_Users):

    find_user_is_verified_true = (
        db.query(User)
        .filter(
            ((User.uname == user.uname) & (User.email == user.email))
            & (User.is_verified == True)
        )
        .first()
    )

    find_user_is_verified_false = (
        db.query(User)
        .filter(
            ((User.uname == user.uname) & (User.email == user.email))
            & (User.is_verified == False)
        )
        .first()
    )

    if find_user_is_verified_true:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="person already exist and already verified with this email and user name",
        )

    if find_user_is_verified_false:

        find_user_is_verified_false.is_active = True
        find_user_is_verified_false.is_deleted = False
        db.add(find_user_is_verified_false)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="person already exist but didn't verified yet !",
        )

    find_user_name = db.query(User).filter(User.uname == user.uname).first()

    if find_user_name:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, detail="User name already taken"
        )

    find_user_email = db.query(User).filter(User.email == user.email).first()

    if find_user_email:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, detail="User email already taken"
        )

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
    return newUser


#------------------------ MODIFIED USER (GIVEN UNAME) --------------------------#

@auth_router.put(
    "/modify_user/{uname}",
    response_model=Get_Users,
    status_code=status.HTTP_200_OK,
)
def put_user(uname: str, user: Update_Users):
    find_user = db.query(User).filter(User.uname == uname ).first()

    if find_user.is_verified==False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not verified yet")

    if not find_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found or User not verified yet")


    hashed_password = pwd_context.hash(user.password)
    find_user.fname = user.fname
    find_user.lname = user.lname
    find_user.password = hashed_password
    pass_checker(user.password, hashed_password)
    db.add(find_user)
    db.commit()
    return find_user


#---------------------------- DELETE USER (GIVEN UNAME) ----------------------#

@auth_router.delete("/delete_user/{uname}")
def delete_user(uname: str):
    find_user = db.query(User).filter(User.uname == uname).first()

    if find_user:
        find_user.is_active = False
        find_user.is_deleted = True
        find_user.is_verified = False
        db.add(find_user)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    return "user deleted successfully"

#------------------------------ GET ALL THE OTPS---------------------------#

@auth_router.get(
    "/get_allopts", response_model=list[All_Otp], status_code=status.HTTP_200_OK
)
def get_all_otp():
    all_otp = db.query(Otp).all()
    print(all_otp)
    if not all_otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="otp table is empty "
        )
    return all_otp


#----------------------------------- GENERATE OTP ---------------------------------#

@auth_router.post("/generate_otp")
def authentication(auth_user: Auth_schema):

    find_user = db.query(User).filter((User.email == auth_user.email)).first()

    if not find_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    random_number = random.randint(100000, 999999)
    print(random_number)

    newOtp = Otp(
        user_id=find_user.id,
        email=auth_user.email,
        otp=str(random_number),
    )
    print(f"\n\n ---------- OTP is ----------- {random_number} ------------\n\n")
    db.add(newOtp)
    db.commit()

    # # otp send to email
    # server.sendmail(
    #     "makvananickfun@gmail.com",
    #     auth_user.email,
    #     f"Your Otp is {random_number} which is valid for 1 minute",
    # )
    # print("mail sent")
    # server.quit()

    return "otp generated successful"


#------------------------- OTP DELETE (FINAL AUTHENTICATION) -----------------------------

@auth_router.post("/final_authentication", status_code=status.HTTP_202_ACCEPTED)
def final_authentication(final_auth: Final_Auth_schema):

    find_user_from_usertable = (
        db.query(User).filter(User.email == final_auth.email).first()
    )

    if not find_user_from_usertable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    find_user_acc_otp = (
        db.query(Otp)
        .filter((Otp.otp == final_auth.otp) & (Otp.email == final_auth.email))
        .first()
    )

    if not find_user_acc_otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="otp and email not found"
        )

    prev_time = find_user_acc_otp.created_at
    curr_time = datetime.utcnow()

    if (curr_time - prev_time) > timedelta(seconds=60):
        db.delete(find_user_acc_otp)
        db.commit()
        return "Otp Expires"

    find_user_from_usertable.is_verified = True
    find_user_from_usertable.is_active = True
    find_user_from_usertable.is_deleted = False

    db.delete(find_user_acc_otp)
    db.commit()

    access_token = get_token(find_user_from_usertable.id,find_user_from_usertable.email,find_user_from_usertable.uname)
    return {"access_token": access_token}

#-------------------------ACCESS THE PROTECTED RESOURCE -----------------#

# OAuth2 scheme
oauth2_scheme_data_access = OAuth2PasswordBearer(tokenUrl="/final_authentication")

@auth_router.post("/protected_resource")
async def protected_resource(token: str = Security(oauth2_scheme_data_access)):
        user_id = decode_token_user_id(token)
        user = db.query(User).filter(User.id == user_id , User.is_verified==True).first()

        if user.is_verified==False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not verified yet")
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

        return {"message": f"Congooo!! you have an acces of very crucial data"}


#---------------------------------RESET PASSWORD TOKEN GENERATION -------------------------------#

@auth_router.post(
    "/reset_password_token_generation", status_code=status.HTTP_202_ACCEPTED
)
def reset_pass_token_generation(entered_email: Reset_Pass_Email):
    find_email_user_table = (
        db.query(User).filter(User.email == entered_email.email,User.is_verified==True).first()
    )
    if find_email_user_table.is_verified==False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User with this email not verified yet")
    if not find_email_user_table:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User with this email not found")
    access_token = get_token(find_email_user_table.id,find_email_user_table.email,find_email_user_table.uname)
    return {"access_token":access_token}



#--------------------------------RESET PASSWORD -----------------------#
# OAuth2 scheme
oauth2_scheme_reset_pass = OAuth2PasswordBearer(tokenUrl="/reset_password_token_generation")

@auth_router.post("/reset_password", status_code=status.HTTP_202_ACCEPTED)
def reset_pass(new_pass: New_Pass, token: str = Security(oauth2_scheme_reset_pass)):
        user_email = decode_token_user_email(token)
        user = db.query(User).filter(User.email == user_email,User.is_verified==True).first()
        if user.is_verified==False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not verified yet")

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

        hashed_password = pwd_context.hash(new_pass.password)
        user.password = hashed_password
        db.add(user)
        db.commit()

        return {"message": f"Your password successfully changed"}


#-------------------------------LOGIN (OTP AND TOKEN GENERATION) -----------------------#
@auth_router.post("/login_otp_generation")
def login_otp_generation(login_field: Login_Schema):

    find_user = (
        db.query(User)
        .filter(
            (User.uname == login_field.uname)
            & ((User.is_active == True) & (User.is_verified==True) & (User.is_deleted == False))
        )
        .first()
    )

    if not find_user:
        return "User not found or User not verified"

    if not pwd_context.verify(login_field.password, find_user.password):
        return "Wrong password entered"

    random_number = random.randint(100000, 999999)
    newOtp = Otp(
        user_id=find_user.id,
        email=find_user.email,
        otp=str(random_number),
    )
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
    access_token = get_token(find_user.id,find_user.email,find_user.uname)
    return {"access_token": access_token}



#--------------------------FINAL LOGIN USING TOKEN AND OTP---------------------#
# OAuth2 scheme
oauth2_login = OAuth2PasswordBearer(tokenUrl="/login_otp_generation")

@auth_router.post("/final_login_auth")
def final_login_auth(enter_otp: Login_OTP, token: str = Security(oauth2_login)):
        user_email = decode_token_user_email(token)

        # Fetch user data using `email_id`
        email_otp = (
            db.query(Otp)
            .filter((Otp.otp == enter_otp.otp) & (Otp.email == user_email))
            .first()
        )

        if not email_otp:
            return "otp incorrect with this email id"

        prev_time = email_otp.created_at
        curr_time = datetime.utcnow()

        if (curr_time - prev_time) > timedelta(seconds=120):
            db.delete(email_otp)
            db.commit()
            return "Otp Expires"

        db.delete(email_otp)
        db.commit()

        return {"message": f"You are Successfully login"}

