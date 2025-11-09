"""Reset immutable_log to fix sequence conflicts"""
import sqlite3

db_path = "databases/grace.db"

print("Resetting immutable_log table...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Clear the immutable_log table
cursor.execute("DELETE FROM immutable_log")
conn.commit()

print(f"Deleted all entries from immutable_log")

# Verify
cursor.execute("SELECT COUNT(*) FROM immutable_log")
count = cursor.fetchone()[0]
print(f"Remaining entries: {count}")

conn.close()

print("\nDone! Backend should start cleanly now.")
print("Run: .venv\\Scripts\\python.exe -m uvicorn backend.main:app --reload")
