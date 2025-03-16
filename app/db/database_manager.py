import sqlite3
import psycopg2
from psycopg2 import errors
from psycopg2.pool import ThreadedConnectionPool
import os
from typing import Optional
import bcrypt
import logging
from contextlib import contextmanager
from functools import wraps
import time
import threading
from cryptography.fernet import Fernet
import base64
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pool settings
MIN_POOL_SIZE = 1
MAX_POOL_SIZE = 5
POOL_TIMEOUT = 30  # seconds

class DatabaseError(Exception):
    """Custom database error class"""
    pass

def handle_db_errors(func):
    """Decorator to handle database errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {str(e)}")
            raise DatabaseError(f"SQLite error: {str(e)}")
        except psycopg2.Error as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            raise DatabaseError(f"PostgreSQL error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise DatabaseError(f"Unexpected error: {str(e)}")
    return wrapper

class DatabaseManager:
    def __init__(self, sqlite_path="data/bughunter.db", pg_config=None):
        """
        Initialize the DatabaseManager.
        
        Args:
            sqlite_path (str): Path to the SQLite database file
            pg_config (dict): PostgreSQL connection configuration
        """
        self.sqlite_path = sqlite_path
        self.pg_config = pg_config
        self.pg_pool = None
        self.pg_conn = None
        self.pg_cursor = None
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
            'sqlite': {
                'path': self.sqlite_path,
                'connected': bool(self.sqlite_conn)
            },
            'postgresql': {
                'configured': bool(self.pg_config),
                'pool_size': self.pg_pool.size if self.pg_pool else 0,
                'connected': bool(self.pg_conn)
            }
        }

    def _create_audit_table(self):
        """Create audit log table if it doesn't exist"""
        with self.transaction():
            if self.pg_conn:
                self.pg_cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        action TEXT NOT NULL,
                        details JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                logger.info("Audit log table created/verified")

    def log_audit(self, user_id: int, action: str, details: dict = None):
        """Log an audit event"""
        if not self.pg_conn:
            return
        try:
            self.pg_cursor.execute("""
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (%s, %s, %s)
            """, (user_id, action, details))
            self.pg_conn.commit()
            logger.debug(f"Audit logged: {action} by user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log audit: {str(e)}")
            raise DatabaseError(f"Audit logging failed: {str(e)}") from e

    def _initialize_encryption(self):
        """Initialize encryption settings"""
        # Generate or load encryption key
        self.encryption_key = os.getenv('DB_ENCRYPTION_KEY')
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
            
            # Initialize PostgreSQL connection pool if config provided
            if self.pg_config:
                self._initialize_pg_pool()
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {str(e)}")
            raise DatabaseError(f"Connection initialization failed: {str(e)}") from e
    
    def _initialize_pg_pool(self):
        """Initialize PostgreSQL connection pool"""
        self.pg_pool = ThreadedConnectionPool(
            minconn=MIN_POOL_SIZE,
            maxconn=MAX_POOL_SIZE,
            **self.pg_config
        )
        logger.info("PostgreSQL connection pool established")
        
        conn = self._get_pg_connection()
        self.pg_conn = conn
        self.pg_cursor = self.pg_conn.cursor()
        self._release_pg_connection(conn)

    def _get_pg_connection(self):
        """Get a connection from the PostgreSQL pool"""
        try:
            conn = self.pg_pool.getconn(timeout=POOL_TIMEOUT)
            conn.autocommit = False
            return conn
        except psycopg2.pool.PoolError as e:
            logger.error(f"Failed to get connection from pool: {str(e)}")
            raise DatabaseError(f"Connection pool error: {str(e)}") from e

    def _release_pg_connection(self, conn):
        """Release a connection back to the PostgreSQL pool"""
        try:
            self.pg_pool.putconn(conn)
        except psycopg2.pool.PoolError as e:
            logger.error(f"Failed to release connection to pool: {str(e)}")
            raise DatabaseError(f"Connection pool error: {str(e)}") from e

    @contextmanager
    def transaction(self):
        """Context manager for handling transactions"""
        try:
            yield
            if self.pg_conn:
                self.pg_conn.commit()
            self.sqlite_conn.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            if self.pg_conn:
                self.pg_conn.rollback()
            self.sqlite_conn.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise DatabaseError(f"Transaction failed: {str(e)}") from e

    @handle_db_errors
    def create_tables(self):
        """Create database tables with error handling"""
        with self.transaction():
            # Create SQLite tables
            self.sqlite_cursor.executescript("""
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

            # Create PostgreSQL tables if connection exists
            if self.pg_conn:
                self.pg_cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        hashed_password TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT,  -- Encrypted field
                        address TEXT,  -- Encrypted field
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE TABLE IF NOT EXISTS roles (
                        id SERIAL PRIMARY KEY,
                        role_name TEXT UNIQUE NOT NULL,
                        permissions JSONB NOT NULL DEFAULT '{}'
                    );
                    
                    CREATE TABLE IF NOT EXISTS user_roles (
                        user_id INTEGER REFERENCES users(id),
                        role_id INTEGER REFERENCES roles(id),
                        PRIMARY KEY (user_id, role_id)
                    );
                    
                    CREATE TABLE IF NOT EXISTS notifications (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        message TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                logger.info("PostgreSQL tables created/verified")

    @handle_db_errors
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            logger.debug("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"Password hashing failed: {str(e)}")
            raise DatabaseError(f"Password hashing failed: {str(e)}") from e

    @handle_db_errors
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            result = bcrypt.checkpw(password.encode(), hashed_password.encode())
            logger.debug("Password verification completed")
            return result
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            raise DatabaseError(f"Password verification failed: {str(e)}") from e

    @handle_db_errors
    def close(self):
        """Close database connections"""
        try:
            if self.sqlite_conn:
                self.sqlite_conn.close()
                self.sqlite_conn = None
                logger.info("SQLite connection closed")
            if self.pg_pool:
                self.pg_pool.closeall()
                self.pg_pool = None
                logger.info("PostgreSQL connection pool closed")
        except Exception as e:
            logger.error(f"Failed to close connections: {str(e)}")
            raise DatabaseError(f"Connection closing failed: {str(e)}") from e

    def __enter__(self):
        return self

    def check_permission(self, user_id: int, permission: str) -> bool:
        """Check if a user has a specific permission"""
        try:
            self.pg_cursor.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM user_roles ur
                    JOIN roles r ON ur.role_id = r.id
                    WHERE ur.user_id = %s AND r.permissions ? %s
                )
            """, (user_id, permission))
            return self.pg_cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Permission check failed: {str(e)}")
            raise DatabaseError(f"Permission check failed: {str(e)}") from e

    def add_permission(self, role_id: int, permission: str) -> None:
        """Add a permission to a role"""
        try:
            self.pg_cursor.execute("""
                UPDATE roles
                SET permissions = permissions || %s
                WHERE id = %s
            """, (permission, role_id))
            self.pg_conn.commit()
        except Exception as e:
            logger.error(f"Failed to add permission: {str(e)}")
            raise DatabaseError(f"Failed to add permission: {str(e)}") from e

    def remove_permission(self, role_id: int, permission: str) -> None:
        """Remove a permission from a role"""
        try:
            self.pg_cursor.execute("""
                UPDATE roles
                SET permissions = permissions - %s
                WHERE id = %s
            """, (permission, role_id))
            self.pg_conn.commit()
        except Exception as e:
            logger.error(f"Failed to remove permission: {str(e)}")
            raise DatabaseError(f"Failed to remove permission: {str(e)}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
