from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from backend.auth import get_current_user
from backend.models import User, async_session


def require_roles(*allowed_roles: str) -> Callable:
    """Return a dependency that enforces the caller has one of the given roles."""

    async def _checker(username: str = Depends(get_current_user)) -> str:
        if not allowed_roles:
            return username

        async with async_session() as session:
            result = await session.execute(
                select(User.role).where(User.username == username)
            )
            role = result.scalar_one_or_none()

        if role is None:
            raise HTTPException(status_code=401, detail="User not found")

        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges",
            )

        return username

    return _checker
