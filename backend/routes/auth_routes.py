from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, constr, field_validator
from datetime import timedelta
from sqlalchemy import select
from ..models import User, async_session
from ..auth import hash_password, verify_and_upgrade_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..security.sanitization import sanitize_text_value
from ..security.rate_limiter import limiter
from ..settings import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

UsernameStr = constr(strip_whitespace=True, min_length=3, max_length=64, regex=r"^[A-Za-z0-9_.-]+$")
PasswordStr = constr(min_length=8, max_length=128)

class UserCreate(BaseModel):
    username: UsernameStr
    password: PasswordStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return sanitize_text_value(value, field="username")

class UserLogin(BaseModel):
    username: UsernameStr
    password: PasswordStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return sanitize_text_value(value, field="username")

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
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
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(user: UserLogin):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == user.username)
        )
        db_user = result.scalar_one_or_none()
        if not db_user or not verify_and_upgrade_password(user.password, db_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # If upgraded to bcrypt, persist
        await session.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
