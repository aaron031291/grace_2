import os
import time

# Delete database
if os.path.exists("grace.db"):
    try:
        os.remove("grace.db")
        print("Database deleted!")
    except:
        print("ERROR: Close the backend server first (Ctrl+C in the backend window)")
        print("Then run this script again")
        exit(1)

time.sleep(1)

# Recreate
from database import SessionLocal, Base, engine
from models import User
from auth import get_password_hash

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create admin user
new_user = User(
    username="admin",
    email="admin@test.com",
    hashed_password=get_password_hash("admin123")
)
db.add(new_user)
db.commit()

print("SUCCESS!")
print("Database recreated with user:")
print("  Username: admin")
print("  Password: admin123")
print("")
print("Now restart the backend: py main.py")

db.close()
