from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import timedelta
from sqlalchemy import select
from ..models import User, async_session
from ..auth import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == user.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
        
        new_user = User(
            username=user.username,
            password_hash=hash_password(user.password),
            password_hash_is_legacy=False,
        )
        session.add(new_user)
        await session.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == user.username)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user or not verify_password(user.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
