# Main FastAPI application
# Contains routes, middleware, and dependencies

import time
import logging
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.responses import JSONResponse

from auth import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    hash_password, verify_password, create_access_token, decode_token
)
from config import USERS_DB


# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app init
app = FastAPI(title="JWT Auth API")


# Middleware - logs every request with processing time
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # this middleware logs HTTP requests and response time
    # pretty useful for debugging and monitoring
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Method={request.method} Path={request.url.path} "
        f"Status={response.status_code} ProcessTime={process_time:.3f}s"
    )
    return response


# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # catches any unhandled exception and returns JSON response
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Dependency - gets current user from JWT token in Authorization header
async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    # extract token from Authorization: Bearer <token> header
    # decode it and validate - if anything fails return 401
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    
    if email not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return email


# Routes

@app.post("/register", response_model=dict)
async def register(user: UserRegister):
    # register endpoint - creates new user account
    # validates email and password using pydantic
    # hashes password before storing in database
    
    if user.email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # hash password and store in memory db
    hashed_pwd = hash_password(user.password)
    USERS_DB[user.email] = {"password": hashed_pwd}
    
    return {"message": "User registered successfully"}


@app.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    # login endpoint - validates credentials and generates JWT token
    # returns access_token if credentials are correct
    
    if user.email not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    stored_user = USERS_DB[user.email]
    if not verify_password(user.password, stored_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # create JWT token with user email as subject
    access_token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=access_token, token_type="bearer")


@app.get("/protected", response_model=UserResponse)
async def protected_route(current_user: str = Depends(get_current_user)):
    # protected route - requires valid JWT token
    # uses dependency injection to validate token and get user
    # returns current user info
    
    return UserResponse(email=current_user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
