import logging
import sys
from PyQt5.QtWidgets import QApplication
from app.config.config import settings
from app.config.config_manager import ConfigManager
from app.main.main_window import MainWindow
from app.factories.manager_factory import ManagerFactory

logger = logging.getLogger("BugHunter")

class Application:
    """
    Main application class for BugHunter.
    Manages the initialization and configuration of various application components.
    """

    def __init__(self, manager_factory: ManagerFactory):
        """
        Initialize the Application.
        Sets up configuration, database, authentication, and other managers.
        """
        self.config = ConfigManager()
        self.managers = manager_factory.create_managers(self.config)

    def apply_migrations(self):
        """
        Apply database migrations.
        """
        self.managers['migration'].apply_migrations()

def initialize_application():
    """
    Initialize the application and apply database migrations.

    Returns:
        Application: The initialized application.
    """
    try:
        manager_factory = ManagerFactory()
        app = Application(manager_factory)
        app.apply_migrations()
        logger.info("All managers initialized successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

def main():
    """
    Main entry point for the BugHunter application.
    Initializes the application, creates the application instance, and starts the event loop.
    """
    try:
        app = initialize_application()
        qt_app = QApplication(sys.argv)
        window = MainWindow(app.managers)
        window.show()
        sys.exit(qt_app.exec_())
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
