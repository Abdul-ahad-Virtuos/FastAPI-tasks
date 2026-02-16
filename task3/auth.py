# Auth module - handles JWT tokens and password hashing
# This is where all the security stuff happens, not in the main app

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator
import re

from config import SECRET_KEY, ALGORITHM, TOKEN_EXPIRATION


# password hashing - bcrypt is used because its secure and stuff
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Schemas - validation models
class UserRegister(BaseModel):
    # email and password for registration
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least 1 number")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain 1 uppercase letter")
        return v


class UserLogin(BaseModel):
    # for login endpoint - email and password required
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    # response when token is created
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    # user info response - no password included!!!
    email: str


# Utility functions for JWT and passwords
def hash_password(password: str) -> str:
    # takes plain password and returns hashed version
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # check if the plain password matches the hashed one
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # creates JWT token with expiration and user subject
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + TOKEN_EXPIRATION
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    # decode JWT token and return claims
    # returns None if invalid or expired
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
