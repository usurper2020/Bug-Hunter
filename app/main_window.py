import sys
import os
import logging
from PyQt6.QtWidgets import (
QMainWindow, QMessageBox, QTabWidget,
QStatusBar, QMenuBar, QAction, QFileDialog
)
from PyQt6 import QtWidgets, QtCore
from dataclasses import dataclass

from app.gui.tabs.report_generator import ReportGeneratorTab
from app.gui.tabs.shodan_tab import ShodanTab
from app.gui.tabs.tool_manager_tab import ToolManagerTab
from app.gui.tabs.wayback_tab import WaybackTab
from app.gui.tabs.ai_chat_tab import AIChatTab
from app.gui.tabs.scope_tab import ScopeTab
from app.gui.tabs.scanner_tab import ScannerTab
from app.services.shodan_integration import ShodanClient


class MainWindow(QMainWindow):
"""Main application window for BugHunter."""
def __init__(self, config_manager=None, auth_manager=None, notification_system=None, website_scanner=None):
super().__init__()
self.setWindowTitle("BugHunter")
self.setGeometry(100, 100, 1200, 800)
        
self.config_manager = config_manager
self.auth_manager = auth_manager or self._initialize_auth_manager()
self.notification_system = notification_system
self.website_scanner = website_scanner

# Initialize main components
self.init_ui()
self.connect_signals()

def _initialize_auth_manager(self):
from app.services.auth_manager import AuthManager
return AuthManager()

def init_ui(self):
"""Initialize the user interface components."""
try:
# Create main tab widget
self.tab_widget = QTabWidget()
self.setCentralWidget(self.tab_widget)

# Initialize and add tabs
self.tool_manager_tab = ToolManagerTab()
self.scanner_tab = ScannerTab()
self.report_tab = ReportGeneratorTab()
self.scope_tab = ScopeTab()
self.shodan_tab = ShodanTab()
self.wayback_tab = WaybackTab()
self.ai_chat_tab = AIChatTab()

self.tab_widget.addTab(self.tool_manager_tab, "Tool Manager")
self.tab_widget.addTab(self.scanner_tab, "Scanner")
self.tab_widget.addTab(self.report_tab, "Reports")
self.tab_widget.addTab(self.scope_tab, "Scope Management")
self.tab_widget.addTab(self.shodan_tab, "Shodan")
self.tab_widget.addTab(self.wayback_tab, "Wayback Machine")
self.tab_widget.addTab(self.ai_chat_tab, "AI Chat")

# Initialize status bar
self.status_bar = QStatusBar()
self.setStatusBar(self.status_bar)

# Initialize menu bar
self.menu_bar = QMenuBar()
self.setMenuBar(self.menu_bar)
self.init_menu()
except Exception as e:
self.show_error_message("UI Initialization Error", f"Failed to initialize UI: {str(e)}")

def init_menu(self):
"""Initialize the menu bar and its actions."""
try:
# Create menu items and actions
file_menu = self.menu_bar.addMenu("File")
edit_menu = self.menu_bar.addMenu("Edit")
view_menu = self.menu_bar.addMenu("View")
help_menu = self.menu_bar.addMenu("Help")

# File menu actions
open_action = QAction("Open", self)
open_action.triggered.connect(self.open_file)
file_menu.addAction(open_action)

save_action = QAction("Save", self)
save_action.triggered.connect(self.save_file)
file_menu.addAction(save_action)

exit_action = QAction("Exit", self)
exit_action.triggered.connect(self.close)
file_menu.addAction(exit_action)

# Edit menu actions
undo_action = QAction("Undo", self)
edit_menu.addAction(undo_action)

redo_action = QAction("Redo", self)
edit_menu.addAction(redo_action)

# View menu actions
toggle_status_bar_action = QAction("Toggle Status Bar", self)
toggle_status_bar_action.setChecked(True)
toggle_status_bar_action.triggered.connect(self.toggle_status_bar)
view_menu.addAction(toggle_status_bar_action)

# Help menu actions
about_action = QAction("About", self)
about_action.triggered.connect(self.show_about_dialog)
help_menu.addAction(about_action)
except Exception as e:
self.show_error_message("Menu Initialization Error", f"Failed to initialize menu: {str(e)}")


