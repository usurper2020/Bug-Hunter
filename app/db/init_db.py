import os
from database_manager import DatabaseManager
from migration_manager import MigrationManager

def initialize_databases():
    # Ensure SQLite database directory exists
    os.makedirs("data", exist_ok=True)
    
    # Load PostgreSQL configuration from environment variables
    pg_config = {
        'dbname': os.getenv('POSTGRES_DB', 'bughunter'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'sslmode': 'require'  # Enforce SSL connections
    }
    
    # Initialize databases
    db_manager = DatabaseManager(
        sqlite_path="data/bughunter.db",
        pg_config=pg_config
    )
    
    # Apply migrations
    migration_manager = MigrationManager(db_manager)
    migration_manager.apply_migrations()
    
    # Create default roles if using PostgreSQL
    if db_manager.pg_conn:
        db_manager.pg_cursor.execute("""
            INSERT INTO roles (role_name) VALUES ('admin')
            ON CONFLICT (role_name) DO NOTHING;
            
            INSERT INTO roles (role_name) VALUES ('user')
            ON CONFLICT (role_name) DO NOTHING;
        """)
        db_manager.pg_conn.commit()
    
    # Create default SQLite settings
    db_manager.sqlite_cursor.execute("""
        INSERT OR IGNORE INTO user_settings (user_id, preferences)
        VALUES (0, '{}');
    """)
    db_manager.sqlite_conn.commit()
    
    db_manager.close()

if __name__ == "__main__":
    initialize_databases()
