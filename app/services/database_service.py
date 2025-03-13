from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import Session as UserSession
import json
import uuid
import hashlib
from fastapi import HTTPException, status
from datetime import datetime

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    def add_user(self, username: str, password: str, email: str) -> User:
        """Add a new user to the database."""
        new_user = User(username=username, password_hash=self.hash_password(password), email=email)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_user(self, user_id: int) -> User:
        """Retrieve a user by their ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def hash_password(self, password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_session(self, user_id: int) -> UserSession:
        """Create a new session for the user."""
        session = UserSession(user_id=user_id, created_at=datetime.utcnow())
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
