from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

"""
Settings Tab Module.

This module provides the GUI interface for managing application settings in the BugHunter application.
"""


class SettingsTab(QWidget):
    """
    Settings tab for the BugHunter application.

    This tab allows users to configure application settings such as API keys, preferences, and more.
    """

    def __init__(self, parent=None):
        """
        Initialize the SettingsTab.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface components.
        """
        layout = QVBoxLayout()

        # API Key Section
        api_key_layout = QVBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key here...")
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

        # Preferences Section
        preferences_layout = QVBoxLayout()
        preferences_layout.addWidget(QLabel("Preferences:"))
        self.dark_mode_checkbox = QCheckBox("Enable Dark Mode")
        preferences_layout.addWidget(self.dark_mode_checkbox)
        layout.addLayout(preferences_layout)

        # Notification Settings
        notification_layout = QVBoxLayout()
        notification_layout.addWidget(QLabel("Notifications:"))
        self.notifications_checkbox = QCheckBox("Enable Notifications")
        notification_layout.addWidget(self.notifications_checkbox)
        layout.addLayout(notification_layout)

        # Proxy Settings
        proxy_layout = QVBoxLayout()
        proxy_layout.addWidget(QLabel("Proxy Settings:"))
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("Enter proxy (e.g., http://proxy:port)")
        proxy_layout.addWidget(self.proxy_input)
        layout.addLayout(proxy_layout)

        # Language Settings
        language_layout = QVBoxLayout()
        language_layout.addWidget(QLabel("Language:"))
        self.language_selector = QComboBox()
        self.language_selector.addItems(
            ["English", "Spanish", "French", "German", "Chinese"]
        )
        language_layout.addWidget(self.language_selector)
        layout.addLayout(language_layout)

        # Auto-Update Settings
        auto_update_layout = QVBoxLayout()
        auto_update_layout.addWidget(QLabel("Auto-Update:"))
        self.auto_update_checkbox = QCheckBox("Enable Auto-Update")
        auto_update_layout.addWidget(self.auto_update_checkbox)
        layout.addLayout(auto_update_layout)

        # Save Button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        """
        Save the current settings.
        """
        api_key = self.api_key_input.text()
        dark_mode = self.dark_mode_checkbox.isChecked()
        notifications = self.notifications_checkbox.isChecked()
        proxy = self.proxy_input.text()
        language = self.language_selector.currentText()
        auto_update = self.auto_update_checkbox.isChecked()

        # Save settings logic here (e.g., save to config file or database)
        print(
            f"API Key: {api_key}, Dark Mode: {dark_mode}, Notifications: {notifications}, Proxy: {proxy}, Language: {language}, Auto-Update: {auto_update}"
        )
