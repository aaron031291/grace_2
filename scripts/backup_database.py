"""Snapshot sqlite databases for backup/testing purposes."""

import argparse
import shutil
from datetime import datetime
from pathlib import Path


def backup(db_path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    target = dest_dir / f"{db_path.stem}-{timestamp}{db_path.suffix}"
    shutil.copy2(db_path, target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup Grace sqlite database")
    parser.add_argument("--db", default="grace.db")
    parser.add_argument("--dest", default="backups")
    args = parser.parse_args()

    target = backup(Path(args.db), Path(args.dest))
    print(f"Backup saved to {target}")


if __name__ == "__main__":
    main()
