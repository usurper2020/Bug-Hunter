from typing import Dict, List, Optional
import json
import logging
import os
import sys
from PyQt6.QtWidgets import (
QMainWindow, QMessageBox, QTabWidget,
QStatusBar, QMenuBar, QAction, QFileDialog
)
from PyQt6 import QtWidgets, QtCore
from dataclasses import dataclass

from app.tabs.report_generator import ReportGeneratorTab
from app.tabs.scanner_tab import ScannerTab
from app.tabs.scope_tab import ScopeTab
from app.tabs.shodan_tab import ShodanTab
from app.tabs.tool_manager_tab import ToolManagerTab
from app.tabs.wayback_tab import WaybackTab


class MainWindow(QMainWindow):
"""Main application window for BugHunter."""
def __init__(self):
super().__init__()
self.setWindowTitle("BugHunter")
self.setGeometry(100, 100, 1200, 800)
self.init_ui()
self.connect_signals()

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

self.tab_widget.addTab(self.tool_manager_tab, "Tool Manager")
self.tab_widget.addTab(self.scanner_tab, "Scanner")
self.tab_widget.addTab(self.report_tab, "Reports")
self.tab_widget.addTab(self.scope_tab, "Scope Management")
self.tab_widget.addTab(self.shodan_tab, "Shodan")
self.tab_widget.addTab(self.wayback_tab, "Wayback Machine")

# Initialize status bar
self.status_bar = QStatusBar()
self.setStatusBar(self.status_bar)

# Initialize menu bar
self.menu_bar = QMenuBar()
self.setMenuBar(self.menu_bar)
self.init_menu()
            
except ImportError as e:
self.handle_import_error(e)
except Exception as e:
self.show_error_message(
"Initialization Error", 
f"Failed to initialize UI components: {str(e)}"
)

def init_menu(self):
"""Initialize the menu bar and its actions."""
try:
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
toggle_status_bar_action.setCheckable(True)
toggle_status_bar_action.setChecked(True)
toggle_status_bar_action.triggered.connect(self.toggle_status_bar)
view_menu.addAction(toggle_status_bar_action)

# Help menu actions
about_action = QAction("About", self)
about_action.triggered.connect(self.show_about_dialog)
help_menu.addAction(about_action)
            
except ImportError as e:
self.handle_import_error(e)
except Exception as e:
self.show_error_message(
"Menu Initialization Error",
f"Failed to initialize menu: {str(e)}"
)

def connect_signals(self):
"""Connect signals between components."""
try:
# Connect tool manager signals
self.tool_manager_tab.tool_installed.connect(
self.scanner_tab.update_tools_list
)
self.tool_manager_tab.tool_removed.connect(
self.scanner_tab.update_tools_list
)

# Connect scanner signals
self.scanner_tab.scan_complete.connect(
self.report_tab.add_scan_result
)
self.scanner_tab.status_message.connect(
self.status_bar.showMessage
)

# Connect scope management signals
self.scope_tab.scope_updated.connect(
self.scanner_tab.update_scan_scope
)
self.scope_tab.status_message.connect(
self.status_bar.showMessage
)

# Connect report generator signals
self.report_tab.report_generated.connect(
self.status_bar.showMessage
)
            
except ImportError as e:
self.handle_import_error(e)
except Exception as e:
self.show_error_message(
"Signal Connection Error",
f"Failed to connect signals: {str(e)}"
)

def open_file(self):
"""Open a file dialog to select a file."""
try:
options = QFileDialog.Options()
file_name, _ = QFileDialog.getOpenFileName(
self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options
)
if file_name:
self.status_bar.showMessage(f"Opened file: {file_name}")
except Exception as e:
self.show_error_message(
"File Open Error",
f"Failed to open file: {str(e)}"
)

def save_file(self):
"""Open a file dialog to save a file."""
try:
options = QFileDialog.Options()
file_name, _ = QFileDialog.getSaveFileName(
self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options
)
if file_name:
self.status_bar.showMessage(f"Saved file: {file_name}")
except Exception as e:
self.show_error_message(
"File Save Error",
f"Failed to save file: {str(e)}"
)

def toggle_status_bar(self, state):
"""Toggle the visibility of the status bar."""
try:
self.status_bar.setVisible(state)
except Exception as e:
self.show_error_message(
"Status Bar Toggle Error",
f"Failed to toggle status bar: {str(e)}"
)

def show_about_dialog(self):
"""Show an about dialog."""
try:
QMessageBox.about(
self,
"About BugHunter",
"BugHunter Version 2.0.0\nDeveloped by BugHunter Team"
)
except Exception as e:
self.show_error_message(
"About Dialog Error",
f"Failed to show about dialog: {str(e)}"
)

def show_error_message(self, title, message):
"""Show an error message dialog."""
QMessageBox.critical(self, title, message)

def handle_import_error(self, error):
"""Handle import errors by attempting to correct import paths."""
try:
import_error_message = str(error)
if "No module named" in import_error_message:
missing_module = import_error_message.split("No module named ")[1].strip("'")
logging.info(f"Attempting to correct import path for missing module: {missing_module}")
# Attempt to correct import path
corrected_path = f"app.{missing_module}"
sys.modules[missing_module] = __import__(corrected_path)
logging.info(f"Successfully corrected import path for module: {missing_module}")
else:
logging.error(f"Unhandled import error: {import_error_message}")
except Exception as e:
logging.error(f"Failed to handle import error: {str(e)}", exc_info=True)
self.show_error_message(
"Import Error",
f"Failed to handle import error: {str(e)}"
)

def update_status(self, message):
"""Update the status bar with a message."""
try:
self.status_bar.showMessage(message)
except Exception as e:
self.show_error_message(
"Status Update Error",
f"Failed to update status: {str(e)}"
)

def closeEvent(self, event):
"""Handle the window close event."""
reply = QMessageBox.question(
self,
'Confirm Exit',
'Are you sure you want to exit?',
QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
QMessageBox.StandardButton.No
)
if reply == QMessageBox.StandardButton.Yes:
event.accept()
else:
event.ignore()


if __name__ == "__main__":
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
