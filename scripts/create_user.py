from database import SessionLocal, Base, engine
from models import User
from auth import get_password_hash

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Check if user exists
existing_user = db.query(User).filter(User.username == "admin").first()
if existing_user:
    print("User 'admin' already exists!")
    print("Use: username='admin', password='admin123'")
else:
    # Create new user
    new_user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123")
    )
    db.add(new_user)
    db.commit()
    print("SUCCESS: User created!")
    print("Username: admin")
    print("Password: admin123")

db.close()
