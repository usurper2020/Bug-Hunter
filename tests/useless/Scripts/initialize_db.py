# initialize_db.py
import os
import sys
from pathlib import Path
import sqlite3
import logging
from datetime import datetime

class DatabaseInitializer:
    def __init__(self):
        # Setup paths
        self.base_dir = Path(__file__).resolve().parent.parent
        self.db_dir = self.base_dir / 'database'
        self.db_path = self.db_dir / 'bughunter.db'
        self.schema_dir = self.base_dir / 'database' / 'schemas'
        
        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Configure logging."""
        log_dir = self.base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'db_init_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_directories(self):
        """Create necessary directories if they don't exist."""
        try:
            self.db_dir.mkdir(exist_ok=True)
            self.schema_dir.mkdir(exist_ok=True)
            self.logger.info("Created necessary directories")
        except Exception as e:
            self.logger.error(f"Error creating directories: {e}")
            raise

    def create_schema_files(self):
        """Create database schema files if they don't exist."""
        schemas = {
            'users.sql': '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''',
            'projects.sql': '''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                );
            ''',
            'vulnerabilities.sql': '''
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT,
                    status TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );
            ''',
            'scans.sql': '''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    scan_type TEXT NOT NULL,
                    status TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    results TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );
            '''
        }

        for filename, schema in schemas.items():
            schema_file = self.schema_dir / filename
            if not schema_file.exists():
                try:
                    with schema_file.open('w') as f:
                        f.write(schema.strip())
                    self.logger.info(f"Created schema file: {filename}")
                except Exception as e:
                    self.logger.error(f"Error creating schema file {filename}: {e}")
                    raise

    def initialize_database(self):
        """Initialize the database with schemas."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute each schema file
            for schema_file in self.schema_dir.glob('*.sql'):
                with schema_file.open() as f:
                    schema = f.read()
                    cursor.execute(schema)
                    self.logger.info(f"Executed schema: {schema_file.name}")
            
            conn.commit()
            conn.close()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise

    def create_test_data(self):
        """Create test data for development."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert test user
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', ('test_user', 'test@example.com', 'hashed_password'))

            # Insert test project
            cursor.execute('''
                INSERT OR IGNORE INTO projects (name, description, created_by)
                VALUES (?, ?, ?)
            ''', ('Test Project', 'A test project', 1))

            conn.commit()
            conn.close()
            self.logger.info("Test data created successfully")

        except Exception as e:
            self.logger.error(f"Error creating test data: {e}")
            raise

    def run(self):
        """Run the complete database initialization process."""
        try:
            self.logger.info("Starting database initialization...")
            self.create_directories()
            self.create_schema_files()
            self.initialize_database()
            self.create_test_data()
            self.logger.info("Database initialization completed successfully!")
            print("\nDatabase initialization completed successfully!")
            print(f"Database location: {self.db_path}")
            print(f"Schema location: {self.schema_dir}")
            print(f"Logs location: {self.base_dir / 'logs'}")
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            print("\nError: Database initialization failed!")
            print(f"Check the logs for details: {self.base_dir / 'logs'}")
            sys.exit(1)

def main():
    initializer = DatabaseInitializer()
    initializer.run()

if __name__ == "__main__":
    main()
