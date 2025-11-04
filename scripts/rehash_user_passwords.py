#!/usr/bin/env python3
"""Bulk rehash user passwords with bcrypt.

This utility upgrades legacy `users.password_hash` values that were previously
stored with SHA-256 into bcrypt hashes. Because password hashes are
one-directional, the plaintext password must be supplied (either inline or via
file) in order to generate the new hash.

Usage examples:

```
# Rehash specific users by providing credentials inline
py scripts/rehash_user_passwords.py --password admin:new-strong-password

# Read credentials from a file (CSV: username,password)
py scripts/rehash_user_passwords.py --password-file creds.csv

# Dry-run to view which accounts *would* be rehashed
py scripts/rehash_user_passwords.py --password admin:pass --dry-run
```

The script only touches accounts where `password_hash_is_legacy` is true or the
stored hash is not recognized as bcrypt. All updated accounts are marked with
`password_hash_is_legacy = False`.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
from typing import Dict

from sqlalchemy import select

from backend.auth import hash_password, is_bcrypt_hash
from backend.models import User, async_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rehash user passwords with bcrypt")
    parser.add_argument(
        "--password",
        action="append",
        metavar="USERNAME:PASSWORD",
        help="Provide plaintext password for a user (may be specified multiple times)",
    )
    parser.add_argument(
        "--password-file",
        type=str,
        help="CSV file with `username,password` rows to use for rehashing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List accounts that would be rehashed without applying changes",
    )
    return parser.parse_args()


def load_passwords(args: argparse.Namespace) -> Dict[str, str]:
    mapping: Dict[str, str] = {}

    if args.password:
        for item in args.password:
            if ":" not in item:
                raise ValueError(f"Invalid --password entry '{item}'. Expected format USERNAME:PASSWORD")
            username, plaintext = item.split(":", 1)
            if not username:
                raise ValueError("Username may not be empty in --password entry")
            mapping[username] = plaintext

    if args.password_file:
        with open(args.password_file, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                username = row[0].strip()
                plaintext = row[1]
                if username:
                    mapping[username] = plaintext

    return mapping


async def rehash_users(password_map: Dict[str, str], dry_run: bool) -> int:
    total_candidates = 0
    updated = 0

    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        for user in users:
            legacy_flag = getattr(user, "password_hash_is_legacy", False)
            legacy_hash = not is_bcrypt_hash(user.password_hash)

            if not (legacy_flag or legacy_hash):
                continue

            total_candidates += 1

            plaintext = password_map.get(user.username)
            if not plaintext:
                print(f"[skip] Missing plaintext for user '{user.username}'")
                continue

            new_hash = hash_password(plaintext)
            user.password_hash = new_hash
            if hasattr(user, "password_hash_is_legacy"):
                user.password_hash_is_legacy = False
            updated += 1

        if dry_run:
            await session.rollback()
        else:
            await session.commit()

    print(f"Checked {len(users)} users; candidates={total_candidates}; updated={updated}")
    if dry_run:
        print("Dry-run mode: no changes were written")
    return updated


def main() -> int:
    args = parse_args()
    password_map = load_passwords(args)

    if not password_map:
        print("No passwords provided; use --password or --password-file")
        return 1

    try:
        updated = asyncio.run(rehash_users(password_map, args.dry_run))
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"Error: {exc}")
        return 1

    return 0 if updated or args.dry_run else 2


if __name__ == "__main__":
    raise SystemExit(main())
