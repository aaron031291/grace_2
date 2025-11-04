import hashlib
import os
import string
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

JWT_SECRET_ENV = "GRACE_JWT_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _legacy_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _is_legacy_hash(hash_value: str) -> bool:
    return len(hash_value) == 64 and all(ch in string.hexdigits for ch in hash_value)


def needs_rehash(hashed_password: str) -> bool:
    if _is_legacy_hash(hashed_password):
        return True
    return pwd_context.needs_update(hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if _is_legacy_hash(hashed_password):
        return _legacy_sha256(plain_password) == hashed_password
    return pwd_context.verify(plain_password, hashed_password)


def get_secret_key() -> str:
    secret = os.getenv(JWT_SECRET_ENV)
    if not secret:
        raise RuntimeError(
            "JWT secret is not configured. Set the GRACE_JWT_SECRET environment variable."
        )
    return secret


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, get_secret_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
