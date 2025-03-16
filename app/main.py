import logging
import sys
from PyQt5.QtWidgets import QApplication
from app.config import settings
from app.db.database_manager import DatabaseManager
from app.db.migration_manager import MigrationManager
from app.auth.auth_manager import AuthManager
from app.auth.role_manager import RoleManager
from app.auth.session import SessionManager
from app.notifications.notification_manager import NotificationManager
from app.api.api_manager import APIManager
from app.security.security_manager import SecurityManager
from app.ai.ai_manager import AIManager
from app.tools.tool_manager import ToolManager
from app.config.config_manager import ConfigManager
from app.main_window import MainWindow

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
        self.session = SessionManager()
        
        # Initialize other managers
        self.notifications = NotificationManager(self.db)
        self.api = APIManager()
        self.security = SecurityManager()
        self.ai = AIManager()
        self.tools = ToolManager()

def initialize_managers():
    """Initialize all application managers"""
    try:
        managers = ApplicationManagers()
        
        # Run database migrations
        managers.migrations.apply_migrations()
        
        logger.info("All managers initialized successfully")
        return managers
        
    except Exception as e:
        logger.error(f"Failed to initialize managers: {str(e)}")
        raise

def main():
    try:
        # Initialize all managers
        managers = initialize_managers()
        
        # Create application instance
        app = QApplication(sys.argv)
        
        # Create main window with initialized managers
        window = MainWindow(managers)
        window.show()
        
        # Start application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
