import os
import psycopg2
from psycopg2 import sql
import bcrypt

class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session  # Use the provided database session

    def authenticate_user(self, username, password):
        """Validate user credentials."""
        with self.db_session.get_cursor(self.db_session) as cursor:
            query = sql.SQL("SELECT password_hash FROM users WHERE username = %s")
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result and self.verify_password(password, result[0]):
                return True
            return False

    def register_user(self, username, password, email=None, name=None, job_title=None, phone=None, address=None, city=None, state=None, zip_code=None, security_question=None, security_answer=None):
        """Register a new user."""  
        # Check if username or email already exists
        with self.db_session.get_cursor(self.db_session) as cursor:
            query = sql.SQL("SELECT COUNT(*) FROM users WHERE username = %s OR email = %s")
            cursor.execute(query, (username, email))
            count = cursor.fetchone()[0]
            if count > 0:
                raise ValueError("Username or email already exists.")
        hashed_password = self.get_password_hash(password)
        with self.db_session.get_cursor(self.db_session) as cursor:
            query = sql.SQL("INSERT INTO users (username, password_hash, email, name, job_title, phone, address, city, state, zip_code, security_question, security_answer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            cursor.execute(query, (username, hashed_password, email, name, job_title, phone, address, city, state, zip_code, security_question, security_answer))
            self.db_session.commit()
            return True

    def verify_password(self, plain_password, hashed_password):
        """Verify a password against its hash."""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def get_password_hash(self, password):
        """Generate a password hash."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def recover_password(self, username, security_answer):
        """Recover password using security question answer."""
        with self.db_session.get_cursor(self.db_session) as cursor:
            query = sql.SQL("SELECT password_hash FROM users WHERE username = %s AND security_answer = %s")
            cursor.execute(query, (username, security_answer))
            result = cursor.fetchone()
            if result:
                return True  # Password recovery successful
            return False  # Password recovery failed