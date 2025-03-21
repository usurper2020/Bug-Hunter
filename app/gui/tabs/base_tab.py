from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal

"""Base tab implementation for the BugHunter application."""

class BaseTab(QWidget):
    """
    Base tab class that all other tabs should inherit from.
    
    Provides common functionality and structure for all tabs.
    """
    
    # Signals
    tab_activated = pyqtSignal()  # Emitted when tab becomes active
    tab_deactivated = pyqtSignal()  # Emitted when tab becomes inactive
    
    def __init__(self, config_manager):
        """
        Initialize the base tab.
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        self.config_manager = config_manager
        self.tab_name = "Base Tab"  # Default name, should be overridden
        self.is_initialized = False
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """
        Set up the base UI components.
        
        This method should be overridden by subclasses to add
        tab-specific UI components.
        """
        # Create main layout
        self.main_layout = QVBoxLayout()
        
        # Add a header label
        self.header_label = QLabel(self.tab_name)
        self.header_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.main_layout.addWidget(self.header_label)
        
        # Set the main layout
        self.setLayout(self.main_layout)
        self._setup_ui()
        self.is_initialized = True
    
    def _setup_ui(self):
        """
        Internal method for UI setup.
        
        This is a placeholder method that should be implemented
        by subclasses if needed.
        """
        # This is a placeholder implementation
        pass

    def connect_signals(self):
        """Connect Qt signals"""
        pass

    def refresh(self):
        """
        Refresh tab content.
        This method should be overridden by derived classes to perform specific refresh operations,
        such as updating displayed data, reloading configurations, or resetting UI elements.
        """
        pass
    
    def show_message(self, title, message, icon=QMessageBox.Icon.Information):
        """
        Display a message box to the user.
        
        Args:
            title (str): The title of the message box
            message (str): The message to display
            icon (QMessageBox.Icon): The icon to display (default: Information)
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec()
    
    def show_error(self, title, message):
        """
        Display an error message to the user.
        
        Args:
            title (str): The title of the error message
            message (str): The error message to display
        """
        self.show_message(title, message, QMessageBox.Icon.Critical)
    
    def is_active(self):
        """
        Check if this tab is currently active/visible.
        
        Returns:
            bool: True if the tab is active, False otherwise
        """
        # This is a placeholder. In a real implementation, this would check
        # if this tab is the currently selected tab in the parent QTabWidget
        return self.isVisible() and self.isEnabled()
    
    def save_state(self):
        """
        Save the current state of the tab.
        
        This method should be overridden by derived classes to save
        their specific state information.
        
        Returns:
            dict: A dictionary containing the tab's state
        """
        return {"tab_name": self.tab_name}
    
    def restore_state(self, state):
        """
        Restore the tab's state from the provided state dictionary.
        
        This method should be overridden by derived classes to restore
        their specific state information.
        
        Args:
            state (dict): A dictionary containing the tab's state
        """
        if "tab_name" in state:
            self.tab_name = state["tab_name"]
            self.header_label.setText(self.tab_name)
    
    def get_name(self):
        """
        Get the name of the tab.
        
        Returns:
            str: The name of the tab
        """
        return self.tab_name
    
    def set_name(self, name):
        """
        Set the name of the tab.
        
        Args:
            name (str): The new name for the tab
        """
        self.tab_name = name
        self.header_label.setText(name)
    
    def set_enabled(self, enabled):
        """
        Enable or disable the tab.
        
        Args:
            enabled (bool): True to enable, False to disable
        """
        self.setEnabled(enabled)
    
    def add_widget(self, widget, stretch=0):
        """
        Add a widget to the main layout.
        
        Args:
            widget (QWidget): The widget to add
            stretch (int): The stretch factor (default: 0)
        """
        self.main_layout.addWidget(widget, stretch)
    
    def add_layout(self, layout, stretch=0):
        """
        Add a layout to the main layout.
        
        Args:
            layout (QLayout): The layout to add
            stretch (int): The stretch factor (default: 0)
        """
        self.main_layout.addLayout(layout, stretch)
    
    def add_spacer(self, size=10):
        """
        Add a vertical spacer to the main layout.
        
        Args:
            size (int): The size of the spacer in pixels (default: 10)
        """
        spacer = QSpacerItem(20, size, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.main_layout.addItem(spacer)
    
    def clear_layout(self, layout):
        """
        Clear all widgets from the specified layout.
        
        Args:
            layout (QLayout): The layout to clear
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
    
    def on_tab_activated(self):
        """
        Called when this tab becomes active.
        
        Override this method in derived classes to perform
        actions when the tab is activated.
        """
        self.tab_activated.emit()
    
    def on_tab_deactivated(self):
        """
        Called when this tab becomes inactive.
        
        Override this method in derived classes to perform
        actions when the tab is deactivated.
        """
        self.tab_deactivated.emit()
