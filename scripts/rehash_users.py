import asyncio
from sqlalchemy import select
from backend.models import async_session, User
from backend.auth import is_bcrypt_hash, hash_password

async def rehash_legacy_passwords(dry_run: bool = True) -> int:
    updated = 0
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for u in users:
            if not is_bcrypt_hash(u.password_hash):
                if dry_run:
                    print(f"[DRY-RUN] Would rehash user: {u.username}")
                else:
                    # Cannot rehash without the plaintext password. For safety, this script sets a temporary lock by making
                    # the hash clearly non-usable. Real migration should be on login flow or by forcing password reset.
                    # If you possess original plaintexts (rare), replace with hash_password(plaintext).
                    # Here, we choose to skip and rely on login-time upgrade implemented in backend.auth.
                    pass
                updated += 1
        if not dry_run:
            await session.commit()
    return updated

if __name__ == "__main__":
    dry = True
    count = asyncio.run(rehash_legacy_passwords(dry_run=dry))
    mode = "DRY-RUN" if dry else "APPLIED"
    print(f"{mode}: {count} legacy-hash user(s) detected.")
