from app.db.database_manager import DatabaseManager
from app.db.migration_manager import MigrationManager
from app.notifications.notification_manager import NotificationManager
from app.api.api_manager import APIManager
from app.security.security_manager import SecurityManager
from app.ai.ai_manager import AIManager
from app.tools.tool_manager import ToolManager
from app.auth.auth_manager import AuthManager
from app.auth.role_manager import RoleManager
from app.auth.session import SessionManager

class ManagerFactory:
    """
    Factory class for creating application managers.
    """

    def create_managers(self, config):
        """
        Create and return a dictionary of application managers.

        Args:
            config (ConfigManager): The configuration manager.

        Returns:
            dict: A dictionary of application managers.
        """
        db_manager = self.create_database_manager(config)
        return {
            'database': db_manager,
            'migration': MigrationManager(db_manager),
            'auth': AuthManager(),
            'role': RoleManager(),
            'session': SessionManager(),
            'notification': NotificationManager(db_manager),
            'api': APIManager(),
            'security': SecurityManager(),
            'ai': AIManager(),
            'tool': ToolManager()
        }

    def create_database_manager(self, config):
        """
        Create and return the database manager.

        Args:
            config (ConfigManager): The configuration manager.

        Returns:
            DatabaseManager: The initialized database manager.
        """
        return DatabaseManager(
            sqlite_path=config.get_config('SQLITE_PATH'),
            pg_dbname=config.get_config('POSTGRES_DB'),
            pg_user=config.get_config('POSTGRES_USER'),
            pg_password=config.get_config('POSTGRES_PASSWORD'),
            pg_host=config.get_config('POSTGRES_HOST'),
            pg_port=config.get_config('POSTGRES_PORT')
        )
