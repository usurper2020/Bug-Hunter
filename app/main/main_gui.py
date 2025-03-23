import logging
import sys
from PyQt5.QtWidgets import QApplication
from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles
from app.db.database_manager import DatabaseManager
from app.db.migration_manager import MigrationManager
from app.auth.role_manager import RoleManager
from app.notifications.notification_manager import NotificationManager
from app.api.api_manager import APIManager
from app.security.security_manager import SecurityManager
from app.ai.ai_manager import AIManager
from app.tools.tool_manager import ToolManager
from app.config.config_manager import ConfigManager
from app.main_window import MainWindow


def initialize_managers():
    # Initialize all necessary managers here
    config_manager = ConfigManager()
    database_manager = DatabaseManager(config_manager)
    migration_manager = MigrationManager(database_manager)
    auth_manager = AuthManager()
    role_manager = RoleManager(database_manager)
    session_manager = SessionManager(database_manager)
    notification_manager = NotificationManager(database_manager)
    api_manager = APIManager()
    security_manager = SecurityManager()
    ai_manager = AIManager()
    tool_manager = ToolManager()

    # Apply database migrations
    migration_manager.apply_migrations()

    return {
        "config_manager": config_manager,
        "database_manager": database_manager,
        "migration_manager": migration_manager,
        "auth_manager": auth_manager,
        "role_manager": role_manager,
        "session_manager": session_manager,
        "notification_manager": notification_manager,
        "api_manager": api_manager,
        "security_manager": security_manager,
        "ai_manager": ai_manager,
        "tool_manager": tool_manager,
    }


def main():
    try:
        # Initialize all managers
        managers = initialize_managers()

        # Create application instance
        app = QApplication(sys.argv)

        # Create main window with initialized managers
        window = MainWindow(managers)
        window.setWindowTitle("BugHunter")
        window.setGeometry(100, 100, 1200, 800)
        window.show()

        # Start application event loop
        sys.exit(app.exec_())

    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
import logging
import sys
from PyQt5.QtWidgets import QApplication
from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles
from app.db.database_manager import DatabaseManager
from app.db.migration_manager import MigrationManager
from app.notifications.notification_manager import NotificationManager
from app.security.security_manager import SecurityManager
from app.ai.ai_manager import AIManager
from app.tools.tool_manager import ToolManager
from app.config.config_manager import ConfigManager
from app.main_window import MainWindow


def initialize_managers():
    # Initialize all necessary managers here
    config_manager = ConfigManager()
    database_manager = DatabaseManager(config_manager)
    migration_manager = MigrationManager(database_manager)
    notification_manager = NotificationManager(database_manager)
    security_manager = SecurityManager()
    ai_manager = AIManager()
    tool_manager = ToolManager()

    # Apply database migrations
    migration_manager.apply_migrations()

    return {
        "config_manager": config_manager,
        "database_manager": database_manager,
        "migration_manager": migration_manager,
        "notification_manager": notification_manager,
        "security_manager": security_manager,
        "ai_manager": ai_manager,
        "tool_manager": tool_manager,
    }


def main():
    try:
        # Initialize all managers
        managers = initialize_managers()

        # Create application instance
        app = QApplication(sys.argv)

        # Create main window with initialized managers
        window = MainWindow(managers)
        window.setWindowTitle("BugHunter")
        window.setGeometry(100, 100, 1200, 800)
        window.show()

        # Start application event loop
        sys.exit(app.exec_())

    except Exception as e:
        logging.error(f"Application startup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
