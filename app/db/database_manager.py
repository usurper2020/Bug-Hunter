import sqlite3
import os
from typing import Optional
import bcrypt
import logging
from contextlib import contextmanager
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, sqlite_path="data/bughunter_logincredentials.db"):
        """
        Initialize the DatabaseManager.

        Args:
            sqlite_path (str): Path to the SQLite database file
        """
        self.sqlite_path = sqlite_path
        self._initialize_encryption()
        self._initialize_connections()
        self.create_tables()
        self._create_audit_table()
        logger.info("DatabaseManager initialized successfully")

    def get_connection_info(self) -> dict:
        """
        Get connection information for debugging and testing purposes.

        Returns:
            dict: Connection information including database types and status
        """
        return {
            "sqlite": {"path": self.sqlite_path, "connected": bool(self.sqlite_conn)}
        }

    def _create_audit_table(self):
        """Create audit log table if it doesn't exist"""
        with self.transaction():
            self.sqlite_cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Audit log table created/verified")

    def log_audit(self, user_id: int, action: str, details: dict = None):
        """Log an audit event"""
        try:
            self.sqlite_cursor.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
            """,
                (user_id, action, details),
            )
            self.sqlite_conn.commit()
            logger.debug(f"Audit logged: {action} by user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log audit: {str(e)}")
            raise DatabaseError(f"Audit logging failed: {str(e)}") from e

    def _initialize_encryption(self):
        """Initialize encryption settings"""
        # Generate or load encryption key
        self.encryption_key = os.getenv("DB_ENCRYPTION_KEY")
        if not self.encryption_key:
            logger.warning("No encryption key found in environment variables")
            self.encryption_key = Fernet.generate_key().decode()
            logger.warning("Generated new encryption key - store this securely!")

        # Initialize Fernet cipher
        self.cipher = Fernet(self.encryption_key.encode())

    def encrypt_field(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode() if data else data

    def decrypt_field(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def _initialize_connections(self):
        """Initialize database connections with error handling"""
        try:
            # Initialize SQLite connection
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.execute("PRAGMA foreign_keys = ON")
            self.sqlite_cursor = self.sqlite_conn.cursor()
            logger.info("SQLite connection established")
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {str(e)}")
            raise DatabaseError(f"Connection initialization failed: {str(e)}") from e

    @contextmanager
    def transaction(self):
        """Context manager for handling transactions"""
        try:
            yield
            self.sqlite_conn.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            self.sqlite_conn.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise DatabaseError(f"Transaction failed: {str(e)}") from e

    def create_tables(self):
        """Create database tables with error handling"""
        with self.transaction():
            # Create SQLite tables
            self.sqlite_cursor.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS collaboration_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    preferences TEXT
                );
            """)
            logger.info("SQLite tables created/verified")

    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            logger.debug("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"Password hashing failed: {str(e)}")
            raise DatabaseError(f"Password hashing failed: {str(e)}") from e

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            result = bcrypt.checkpw(password.encode(), hashed_password.encode())
            logger.debug("Password verification completed")
            return result
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            raise DatabaseError(f"Password verification failed: {str(e)}") from e

    def close(self):
        """Close database connections"""
        try:
            if self.sqlite_conn:
                self.sqlite_conn.close()
                self.sqlite_conn = None
                logger.info("SQLite connection closed")
        except Exception as e:
            logger.error(f"Failed to close connections: {str(e)}")
            raise DatabaseError(f"Connection closing failed: {str(e)}") from e

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.connection.close()
