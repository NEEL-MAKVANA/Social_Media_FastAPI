from fastapi import FastAPI, HTTPException, status, Depends, Security
from pydantic import BaseModel
from database import SessionLocal
from models import User, Otp
from passlib.context import CryptContext
import smtplib
from datetime import datetime, timedelta
import random
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

# from typing import Dict, List


# auth-using-toke-global variable

# Secret key to sign the JWT
SECRET_KEY = "nk168"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# SMTP server setup
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login("makvananickfun@gmail.com", "reatchmqofwmjpfg")


app = FastAPI(title="User Authentication System")
db = SessionLocal()

# Create a PassLib context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# check whether the hash password and user entered password is same or not?


def pass_checker(user_pass, hash_pass):
    if pwd_context.verify(user_pass, hash_pass):
        print("\n\n***********both password are same********\n\n")
        return True
    else:
        raise HTTPException(status_code=401, detail="Password is incorrect")


class OurBasemodel(BaseModel):
    class Config:
        from_attributes = True


class Users(BaseModel):
    fname: str
    lname: str
    uname: str
    email: str
    password: str


class Update_Users(BaseModel):
    fname: str
    lname: str
    password: str


class Print_user(BaseModel):
    fname: str
    lname: str
    uname: str
    email: str
    isverified: bool


class Auth_schema(BaseModel):
    email: str


class Final_Auth_schema(BaseModel):
    email: str
    otp: str


class All_Otp(BaseModel):
    email: str
    otp: str
    attempts: int


class Reset_Pass_Email(BaseModel):
    email: str


class New_Pass(BaseModel):
    password: str


class Login_Schema(BaseModel):
    uname: str
    password: str


class Login_OTP(BaseModel):
    otp: str


# get all user which has isactive=True and isdeleted=False and isverified==True
@app.get("/", response_model=list[Print_user], status_code=status.HTTP_200_OK)
def get_all_user():
    get_all = db.query(User).filter(
        (User.isactive == True) & (User.isdeleted == False) & (User.isverified == True)
    )

    print(get_all)
    return get_all


# post the new user
@app.post("/add_user", response_model=Users, status_code=status.HTTP_200_OK)
def add_user(user: Users):

    find_user_isverified_true = (
        db.query(User)
        .filter(
            ((User.uname == user.uname) & (User.email == user.email))
            & (User.isverified == True)
        )
        .first()
    )

    find_user_isverified_false = (
        db.query(User)
        .filter(
            ((User.uname == user.uname) & (User.email == user.email))
            & (User.isverified == False)
        )
        .first()
    )

    if find_user_isverified_true:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="person already exist and already verified with this email id and userid",
        )

    if find_user_isverified_false:

        find_user_isverified_false.isactive = True
        find_user_isverified_false.isdeleted = False
        db.add(find_user_isverified_false)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="person already exist but didnt verified yet !",
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

    hashed_password = pwd_context.hash(user.password)
    print(f"\n\nthe hash password is***********************{hashed_password}\n\n")
    newUser = User(
        fname=user.fname,
        lname=user.lname,
        uname=user.uname,
        email=user.email,
        password=hashed_password,
    )

    pass_checker(user.password, hashed_password)
    db.add(newUser)
    db.commit()
    return newUser


# modified user (given uname )


@app.put(
    "/modify_user/{uname}",
    response_model=Users,
    status_code=status.HTTP_200_OK,
)
def put_user(uname: str, user: Update_Users):
    find_user = db.query(User).filter(User.uname == uname).first()

    if not find_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    hashed_password = pwd_context.hash(user.password)
    find_user.fname = user.fname
    find_user.lname = user.lname
    find_user.password = hashed_password
    pass_checker(user.password, hashed_password)
    db.add(find_user)
    db.commit()
    return find_user


# delete user (given uname)
@app.delete("/delete_user/{uname}")
def delete_user(uname: str):
    find_user = db.query(User).filter(User.uname == uname).first()

    if find_user:

        find_user.isactive = False
        find_user.isdeleted = True
        find_user.isverified = False
        # db.delete(find_user)
        db.add(find_user)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return "user deleted successfully"


# otp section


# get all the otps


@app.get("/get_allopts", response_model=list[All_Otp], status_code=status.HTTP_200_OK)
def get_all_otp():
    all_otp = db.query(Otp).all()
    print(all_otp)
    if not all_otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="otp table is empty "
        )
    return all_otp


# post otp


@app.post("/generate_otp")
def authentication(auth_user: Auth_schema):

    find_user = db.query(User).filter((User.email == auth_user.email)).first()

    if not find_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # generate otp

    random_number = random.randint(100000, 999999)
    print(random_number)

    newOtp = Otp(
        user_id=find_user.id,
        email=auth_user.email,
        otp=str(random_number),
    )
    print(f"\n\n ********** OTP is ********** {random_number} *********\n\n")
    db.add(newOtp)
    db.commit()

    # otp send to email
    server.sendmail(
        "makvananickfun@gmail.com",
        auth_user.email,
        f"Your Otp is {random_number} which is valid for 1 minute",
    )
    print("mail sent")
    server.quit()
    # global otp_timer
    # otp_timer = datetime.now() + timedelta(minutes=1)  # for one minute
    return "otp generation successfull"


# otp delete (final authentication)


@app.post("/final_authentication", status_code=status.HTTP_202_ACCEPTED)
def final_authentication(final_auth: Final_Auth_schema):

    find_user_from_usertable = (
        db.query(User).filter(User.email == final_auth.email).first()
    )

    find_user_acc_otp = (
        db.query(Otp)
        .filter((Otp.otp == final_auth.otp) & (Otp.email == final_auth.email))
        .first()
    )
    prev_time = find_user_acc_otp.created_at
    print(prev_time)

    curr_time = datetime.utcnow()

    if (curr_time - prev_time) > timedelta(seconds=60):
        db.delete(find_user_acc_otp)
        db.commit()
        return "Otp Expires"

    if not find_user_acc_otp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    find_user_from_usertable.isverified = True
    find_user_from_usertable.isactive = True
    find_user_from_usertable.isdeleted = False
    db.delete(find_user_acc_otp)
    db.commit()

    # payload = {"user_id": find_user_from_usertable.id}
    payload = {
        "user_id": find_user_from_usertable.id,
        "exp": datetime.utcnow() + timedelta(minutes=10),
    }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(type(access_token))

    return {"access_token": access_token}
    # return "Authentication successful"


# OAuth2 scheme
oauth2_scheme_data_access = OAuth2PasswordBearer(tokenUrl="/protected_resource")


@app.post("/protected_resource")
async def protected_resource(token: str = Security(oauth2_scheme_data_access)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        print(user_id)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

        # Fetch user data using `user_id`
        user = db.query(User).filter(User.id == user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return {"message": f"Congooo!! you have an acces of very crucial data"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )


@app.post("/reset_password_token_generation", status_code=status.HTTP_202_ACCEPTED)
def reset_pass_token_generation(entered_email: Reset_Pass_Email):
    find_email_user_table = (
        db.query(User).filter(User.email == entered_email.email).first()
    )
    if not find_email_user_table:
        return "oops! email not found "
    email = find_email_user_table.email
    payload = {
        "user_email": email,
        "exp": datetime.utcnow() + timedelta(minutes=10),
    }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return access_token


# OAuth2 scheme
oauth2_scheme_reset_pass = OAuth2PasswordBearer(tokenUrl="/reset_password")


@app.post("/reset_password", status_code=status.HTTP_202_ACCEPTED)
def reset_pass(new_pass: New_Pass, token: str = Security(oauth2_scheme_reset_pass)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email_id = payload.get("user_email")
        # print(user_id)
        if not email_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

        # Fetch user data using `email_id`
        user = db.query(User).filter(User.email == email_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        hashed_password = pwd_context.hash(new_pass.password)
        user.password = hashed_password
        db.add(user)
        db.commit()

        return {"message": f"Your password successfully changed"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )


@app.post("/login_otp_generation")
def login_otp_generation(login_field: Login_Schema):

    find_user = (
        db.query(User)
        .filter(
            (User.uname == login_field.uname)
            & ((User.isactive == True) & (User.isdeleted == False))
        )
        .first()
    )
    # breakpoint()
    # print(find_user)
    # return "hi"

    if not find_user:
        return "User not found"

    if not pwd_context.verify(login_field.password, find_user.password):
        return "Wrong password entered"

    random_number = random.randint(100000, 999999)
    newOtp = Otp(
        user_id=find_user.id,
        email=find_user.email,
        otp=str(random_number),
    )
    print(f"\n\n ********** OTP is ********** {random_number} *********\n\n")
    db.add(newOtp)
    db.commit()

    server.sendmail(
        "makvananickfun@gmail.com",
        find_user.email,
        f"Your Otp is {random_number} which is valid for 1 minute",
    )
    print("mail sent")
    server.quit()

    payload = {
        "user_email": find_user.email,
        "exp": datetime.utcnow() + timedelta(minutes=10),
    }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(type(access_token))

    return {"access token": access_token}


# OAuth2 scheme
oauth2_login = OAuth2PasswordBearer(tokenUrl="/login_otp_generation")


@app.post("/final_login_auth")
def final_login_auth(enter_otp: Login_OTP, token: str = Security(oauth2_login)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email_id = payload.get("user_email")
        # print(user_id)
        if not email_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

        # Fetch user data using `email_id`
        email_otp = (
            db.query(Otp)
            .filter((Otp.otp == enter_otp.otp) & (Otp.email == email_id))
            .first()
        )

        if not email_otp:
            return "otp incorrect with this email id"

        prev_time = email_otp.created_at
        curr_time = datetime.utcnow()

        if (curr_time - prev_time) > timedelta(seconds=60):
            db.delete(email_otp)
            db.commit()
            return "Otp Expires"

        db.delete(email_otp)
        db.commit()

        return {"message": f"You are Successfully login"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )
