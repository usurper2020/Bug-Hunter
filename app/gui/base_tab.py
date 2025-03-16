from PyQt5.QtWidgets import QWidget, QLabel
import logging

class BaseTab(QWidget):
    """Base class for all tabs in the application"""
    
    def __init__(self, managers, tab_name: str, parent=None):
        super().__init__(parent)
        self.managers = managers
        self.tab_name = tab_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize UI components
        self._setup_ui()
        
        self.logger.info(f"Initialized {self.tab_name} tab")

    def _setup_ui(self):
        """Setup the tab's UI components"""
        raise NotImplementedError("Subclasses must implement _setup_ui")

    def cleanup(self):
        """Clean up resources when tab is closed"""
        self.logger.info(f"Cleaning up {self.tab_name} tab")
        # Subclasses can override to implement specific cleanup logic

    def refresh(self):
        """Refresh tab content"""
        self.logger.info(f"Refreshing {self.tab_name} tab")
        # Subclasses can override to implement refresh logic

from .base_tab import BaseTab

class ExampleTab(BaseTab):
    """Example implementation of a tab"""

    def _setup_ui(self):
        """Setup the tab's UI components"""
        self.label = QLabel("Example Tab", self)
        self.label.move(50, 50)
