import importlib
import os
from database_manager import DatabaseManager
from pathlib import Path

class MigrationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.migrations_dir = Path(__file__).parent / 'migrations'
        
    def get_applied_migrations(self):
        """Get list of already applied migrations"""
        if self.db_manager.pg_conn:
            self.db_manager.pg_cursor.execute("SELECT name FROM migrations ORDER BY id")
            return [row[0] for row in self.db_manager.pg_cursor.fetchall()]
        else:
            self.db_manager.sqlite_cursor.execute("SELECT name FROM migrations ORDER BY id")
            return [row[0] for row in self.db_manager.sqlite_cursor.fetchall()]

    def apply_migrations(self):
        """Apply all pending migrations"""
        applied = self.get_applied_migrations()
        
        # Get all migration files
        migration_files = sorted([
            f for f in os.listdir(self.migrations_dir)
            if f.endswith('.py') and f != '__init__.py'
        ])
        
        for migration_file in migration_files:
            if migration_file not in applied:
                self._apply_migration(migration_file)

    def _apply_migration(self, migration_file):
        """Apply a single migration"""
        module_name = migration_file[:-3]
        module = importlib.import_module(f'app.db.migrations.{module_name}')
        
        # Apply migration
        module.apply_migration(self.db_manager)
        
        # Record migration
        if self.db_manager.pg_conn:
            self.db_manager.pg_cursor.execute(
                "INSERT INTO migrations (name) VALUES (%s)",
                (migration_file,)
            )
            self.db_manager.pg_conn.commit()
        else:
            self.db_manager.sqlite_cursor.execute(
                "INSERT INTO migrations (name) VALUES (?)",
                (migration_file,)
            )
            self.db_manager.sqlite_conn.commit()
