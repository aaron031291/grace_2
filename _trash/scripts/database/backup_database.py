#!/usr/bin/env python3
"""
Backup the database to a timestamped artifact.
- Supports SQLite by copying the DB file.
- For PostgreSQL, attempts to call `pg_dump` if available.
- Optionally uploads to S3 if AWS credentials are configured and boto3 is installed.

Usage:
  py scripts/backup_database.py [--out-dir backups]

Environment:
  DATABASE_URL   SQLAlchemy URL (e.g., sqlite+aiosqlite:///./grace.db or postgresql://user:pass@host/db)
  AWS_S3_BUCKET  (optional) S3 bucket name to upload backup
  AWS_S3_PREFIX  (optional) prefix/path inside bucket
"""
import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_OUT = Path("backups")


def get_output_dir() -> Path:
    out = None
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        out = Path(sys.argv[1])
    else:
        # look for --out-dir option
        for i, a in enumerate(sys.argv):
            if a in {"--out-dir", "-o"} and i + 1 < len(sys.argv):
                out = Path(sys.argv[i + 1])
                break
    return out or DEFAULT_OUT


def backup_sqlite(db_url: str, out_dir: Path) -> Path:
    # formats like sqlite:///./grace.db or sqlite+aiosqlite:///./grace.db
    path = db_url.split("///", 1)[-1]
    if path.startswith('/') and os.name == 'nt':
        # strip leading slash on Windows (e.g., /C:/path)
        path = path.lstrip('/')
    src = Path(path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"SQLite DB file not found: {src}")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    dest = out_dir / f"sqlite_backup_{ts}{src.suffix or '.db'}"
    shutil.copy2(src, dest)
    return dest


def backup_postgres(db_url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    dest = out_dir / f"postgres_backup_{ts}.sql"
    # try to call pg_dump
    try:
        print("[backup] Attempting pg_dump...")
        subprocess.run(["pg_dump", db_url, "-f", str(dest)], check=True)
        return dest
    except Exception as e:
        # fallback: warn and create a marker file
        marker = out_dir / f"postgres_backup_{ts}.INFO.txt"
        marker.write_text(
            "pg_dump not available or failed. Configure pg_dump or run backup in infra pipeline.\n"
            f"Error: {e}\n",
            encoding='utf-8'
        )
        return marker


def maybe_upload_s3(file_path: Path) -> None:
    bucket = os.getenv("AWS_S3_BUCKET")
    if not bucket:
        return
    prefix = os.getenv("AWS_S3_PREFIX", "grace/backups")
    try:
        import boto3  # type: ignore
        s3 = boto3.client('s3')
        key = f"{prefix.rstrip('/')}/{file_path.name}"
        s3.upload_file(str(file_path), bucket, key)
        print(f"[backup] Uploaded to s3://{bucket}/{key}")
    except ModuleNotFoundError:
        print("[backup] boto3 not installed; skipping S3 upload. Add boto3 to requirements if desired.")
    except Exception as e:
        print(f"[backup] S3 upload failed: {e}")


def main() -> int:
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./grace.db")
    out_dir = get_output_dir()
    kind = db_url.split(":", 1)[0]
    if kind.startswith("sqlite"):
        artifact = backup_sqlite(db_url, out_dir)
    elif kind.startswith("postgresql") or kind.startswith("postgres"):
        artifact = backup_postgres(db_url, out_dir)
    else:
        print(f"[backup] Unsupported DATABASE_URL scheme: {kind}")
        return 2
    print(f"[backup] Created artifact: {artifact}")
    maybe_upload_s3(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
