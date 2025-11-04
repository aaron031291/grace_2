"""Export immutable audit log entries for compliance reviews."""

import argparse
import asyncio
import json
from datetime import datetime, timedelta

from sqlalchemy import select

from backend.immutable_log import ImmutableLogEntry
from backend.models import async_session


async def export(path: str, hours: int) -> None:
    since = datetime.utcnow() - timedelta(hours=hours)

    async with async_session() as session:
        result = await session.execute(
            select(ImmutableLogEntry)
            .where(ImmutableLogEntry.timestamp >= since)
            .order_by(ImmutableLogEntry.timestamp.asc())
        )
        entries = result.scalars().all()

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(
            [
                {
                    "sequence": entry.sequence,
                    "actor": entry.actor,
                    "action": entry.action,
                    "resource": entry.resource,
                    "subsystem": entry.subsystem,
                    "result": entry.result,
                    "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
                }
                for entry in entries
            ],
            fh,
            indent=2,
        )

    print(f"Exported {len(entries)} entries to {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export immutable log entries")
    parser.add_argument("--output", default="reports/audit_log.json")
    parser.add_argument("--hours", type=int, default=24)
    args = parser.parse_args()

    asyncio.run(export(args.output, args.hours))


if __name__ == "__main__":
    main()
