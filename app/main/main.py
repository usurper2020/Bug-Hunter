"""Main module for the BugHunter application.
"""

import logging
import sys
from PyQt5.QtWidgets import QApplication
from app.config import settings
from app.db.database_manager import DatabaseManager
from app.db.migration_manager import MigrationManager
from app.auth.auth_manager import AuthManager
from app.auth.role_manager import RoleManager
from app.notifications.notification_manager import NotificationManager
from app.api.api_manager import APIManager
from app.security.security_manager import SecurityManager
from app.ai.ai_manager import AIManager
from app.tools.tool_manager import ToolManager
from app.config.config_manager import ConfigManager
from app.login_gui import LoginGUI  # Changed to absolute import
from app.main_gui import MainGUI  # Changed to absolute import
from app.auth.auth_service import AuthService  # Changed to absolute import
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicationManagers:
    """Container for all application managers"""
    def __init__(self):
        # Initialize configuration first
        self.config = ConfigManager()
        
        # Initialize database components
        self.db = DatabaseManager(
            sqlite_path=settings.SQLITE_PATH,
            pg_config={
                'dbname': settings.POSTGRES_DB,
                'user': settings.POSTGRES_USER,
                'password': settings.POSTGRES_PASSWORD,
                'host': settings.POSTGRES_HOST,
                'port': settings.POSTGRES_PORT
            }
        )
        self.migrations = MigrationManager(self.db)
        
        # Initialize authentication components
        self.auth = AuthManager()
        self.roles = RoleManager()
        
        # Initialize other managers
        self.notifications = NotificationManager(self.db)
        self.api = APIManager()
        self.security = SecurityManager()
        self.ai = AIManager()
        self.tools = ToolManager()

def initialize_managers(db_session):
    """Initialize all application managers"""
    try:
        managers = ApplicationManagers()
        
        # Run database migrations
        managers.migrations.apply_migrations()
        
        logger.info("All managers initialized successfully")
        return managers
        
    except Exception as e:
        logger.error("Failed to initialize managers: %s", str(e))
        raise

def initialize_and_start_app(app, db_session):
    """Initialize managers and start the main GUI after successful login"""
    managers = initialize_managers(db_session)
    window = MainGUI(managers)
    window.show()

def main():
    try:
        app = QApplication(sys.argv)

        def on_login_success():
            initialize_and_start_app(app, db_session)

        # Create a database engine for PostgreSQL
        engine = create_engine(f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}')
        Session = sessionmaker(bind=engine)
        db_session = Session()

        auth_service = AuthService(db_session)  # Pass the database session
        login_window = LoginGUI(on_login_success=on_login_success, auth_service=auth_service)
        login_window.show()

        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error("Application startup failed: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()