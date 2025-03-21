import os
import json
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)
from app.gui.tabs.base_tab import BaseTab

class BugBountyTargetTab(BaseTab):
    """Tab for managing bug bounty targets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bug Bounty Targets")
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface components for the tab."""
        layout = QVBoxLayout(self)

        # Target input
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target URL")
        layout.addWidget(QLabel("Target URL:"))
        layout.addWidget(self.target_input)

        # Add target button
        self.add_button = QPushButton("Add Target")
        self.add_button.clicked.connect(self.add_target)
        layout.addWidget(self.add_button)

        # Target list
        self.target_list = QListWidget()
        layout.addWidget(self.target_list)

        self.setLayout(layout)

    def add_target(self):
        """Add a new target to the list."""
        if target_url := self.target_input.text().strip():
            self.target_list.addItem(QListWidgetItem(target_url))
            self.target_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a target URL.")

    def get_targets(self):
        """Retrieve the list of targets."""
        targets = []
        targets.extend(self.target_list.item(index).text() for index in range(self.target_list.count()))
        return targets
