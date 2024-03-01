from pydantic import BaseModel


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
    is_verified: bool


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
