"""Purge expired operational data to enforce retention policies."""

import argparse
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import delete

from backend.models import ChatMessage, async_session
from backend.governance_models import AuditLog


async def purge(days: int) -> None:
    cutoff = datetime.utcnow() - timedelta(days=days)

    async with async_session() as session:
        chat_result = await session.execute(
            delete(ChatMessage).where(ChatMessage.created_at < cutoff)
        )
        audit_result = await session.execute(
            delete(AuditLog).where(AuditLog.created_at < cutoff)
        )
        await session.commit()

    print("Purged records older than", cutoff.isoformat())
    print(f"  Chat messages removed: {chat_result.rowcount or 0}")
    print(f"  Audit logs removed:    {audit_result.rowcount or 0}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Purge historical data")
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Retention window in days (default: 90)",
    )
    args = parser.parse_args()

    asyncio.run(purge(args.days))


if __name__ == "__main__":
    main()
