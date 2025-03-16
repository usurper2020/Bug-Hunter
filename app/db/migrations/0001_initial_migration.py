from database_manager import DatabaseManager

def apply_migration(db_manager):
    # Create migrations table to track applied migrations
    if db_manager.pg_conn:
        db_manager.pg_cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        db_manager.pg_conn.commit()

    db_manager.sqlite_cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    db_manager.sqlite_conn.commit()

def rollback_migration(db_manager):
    # Remove migrations table (for testing purposes)
    if db_manager.pg_conn:
        db_manager.pg_cursor.execute("DROP TABLE IF EXISTS migrations")
        db_manager.pg_conn.commit()

    db_manager.sqlite_cursor.execute("DROP TABLE IF EXISTS migrations")
    db_manager.sqlite_conn.commit()
