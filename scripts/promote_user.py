"""Assign a role to an existing Grace user."""

import argparse
import asyncio

from sqlalchemy import select

from backend.models import User, async_session


async def promote(username: str, role: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            raise SystemExit(f"User '{username}' not found")

        user.role = role
        await session.commit()

    print(f"Updated {username} -> role={role}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Assign or update a user role")
    parser.add_argument("username")
    parser.add_argument("role", choices=["admin", "analyst", "user", "viewer"])
    args = parser.parse_args()

    asyncio.run(promote(args.username, args.role))


if __name__ == "__main__":
    main()
