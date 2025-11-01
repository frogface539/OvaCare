import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging
from auth import auth_router

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "placeholder_secret_key") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 
app.mount("/static", StaticFiles(directory="static"), name="static")

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    
    return pwd_context.hash(truncated_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
   
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


TEMP_USER_DATABASE = {} 


class User(BaseModel):
    username: str
    email: EmailStr

class UserSignup(BaseModel):
    username: str = Field(..., example="patient_pcos", description="username for signup")
    email: EmailStr = Field(..., example="user@example.com", description="Valid email address")
    password: str = Field(..., example="SecurePassword123", description="Strong password (min 8 chars)")

class UserLogin(BaseModel):
    username: str = Field(..., example="patient_pcos", description="Your registered username")
    password: str = Field(..., example="SecurePassword123", description="Your password")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@app.get("/")
def index():
    return FileResponse("frontend.html")

app.include_router(auth_router)

@auth_router.post("/signup", response_model=User, status_code=201)
def signup(user: UserSignup):
   
   if user.username in TEMP_USER_DATABASE:
        raise HTTPException(status_code=400, detail="Username already registered")
   
   if any(u.get("email") == user.email for u in TEMP_USER_DATABASE.values()):
        raise HTTPException(status_code=400, detail="Email already registered")

   hashed_password = get_password_hash(user.password)

   new_user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
   }
    
    
   TEMP_USER_DATABASE[user.username] = new_user_data

    
   logger.info(f" ✅New user signed up: {user.username} ({user.email})")
    
   return User(**new_user_data)


@auth_router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    
    username = form_data.username
    password = form_data.password

    if username not in TEMP_USER_DATABASE:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    user_data = TEMP_USER_DATABASE[username]
    if not verify_password(password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    
    logger.info(f"🔓User logged in: {username}")
    
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    if token_data.username not in TEMP_USER_DATABASE:
        raise credentials_exception
    
    return TEMP_USER_DATABASE[token_data.username]

