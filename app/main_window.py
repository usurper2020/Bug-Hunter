import sys
import os
import importlib
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, 
                           QTabWidget, QWidget)
from PyQt5.QtCore import Qt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, managers):
        super().__init__()
        self.managers = managers
        
        # Set up main window
        self.setWindowTitle("BugHunter")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create tab widget
"""Main application window for BugHunter."""
def __init__(self, config_manager=None, auth_manager=None, notification_system=None, website_scanner=None):
        
        # Load and initialize tabs
        self._load_tabs()
        
        logger.info("Main window initialized with dynamic tabs")

    def _load_tabs(self):
        """Dynamically load and initialize tabs from the tabs directory"""
        tabs_dir = os.path.join(os.path.dirname(__file__), 'gui', 'tabs')
        
        if not os.path.exists(tabs_dir):
            logger.error(f"Tabs directory not found: {tabs_dir}")
            return
            
        for filename in os.listdir(tabs_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                try:
                    # Import the tab module
                    module_name = filename[:-3]
                    module = importlib.import_module(f'app.gui.tabs.{module_name}')
                    
                    # Get the tab class (assuming naming convention TabClassName)
                    tab_class = getattr(module, f'{module_name.capitalize()}Tab')
                    
                    # Create tab instance with managers
                    tab_instance = tab_class(managers=self.managers)
                    
                    # Add tab to the tab widget
                    self.tab_widget.addTab(tab_instance, tab_instance.tab_name)
                    
                    logger.info(f"Loaded tab: {module_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load tab {filename}: {str(e)}")

    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Application shutting down")
        
        # Clean up resources
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'cleanup'):
                tab.cleanup()
                
        self.managers.db.close()
        event.accept()
