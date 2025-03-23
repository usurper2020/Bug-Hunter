import re
import os
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

class UserManagementDialog(QDialog):
    """Dialog for managing users"""

    user_updated = QtCore.pyqtSignal()  # Signal emitted when user list is updated

    def __init__(self, auth_manager, role_manager, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.role_manager = role_manager
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        """Set up the user management dialog UI"""
        self.setWindowTitle("User Management")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # User list
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Username", "Email", "Role", "Actions"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.user_table)

        # Add user section
        add_section = QVBoxLayout()
        add_section.addWidget(QLabel("Add New User"))

        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        add_section.addLayout(username_layout)

        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        add_section.addLayout(password_layout)

        # Email field
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        add_section.addLayout(email_layout)

        # Role selection
        role_layout = QHBoxLayout()
        role_label = QLabel("Role:")
        self.role_combo = QComboBox()
        self.load_roles()
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        add_section.addLayout(role_layout)

        # Add user button
        self.add_button = QPushButton("Add User")
        add_section.addWidget(self.add_button)

        layout.addLayout(add_section)

        # Close button
        self.close_button = QPushButton("Close")
        layout.addWidget(self.close_button)

        # Connect signals
        self.add_button.clicked.connect(self.add_user)
        self.close_button.clicked.connect(self.accept)

        # Set style
        self.set_style_sheet()

    
def load_roles(self):
    """Load available roles into role combo box"""
    result = self.role_manager.get_all_roles()
    if result["status"] == "success":
        self.role_combo.clear()
        for role_id, role_info in result["roles"].items():
            self.role_combo.addItem(role_info["name"], role_id)

    def load_users(self):
        """Load users into table"""
        with self.auth_manager.db_session.get_cursor(self.auth_manager.db_session) as cursor:
            query = "SELECT username, email, role FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            
            self.user_table.setRowCount(0)  # Clear existing rows
            for user in users:
                row_position = self.user_table.rowCount()
                self.user_table.insertRow(row_position)
                self.user_table.setItem(row_position, 0, QTableWidgetItem(user[0]))  # Username
                self.user_table.setItem(row_position, 1, QTableWidgetItem(user[1]))  # Email
                self.user_table.setItem(row_position, 2, QTableWidgetItem(user[2]))  # Role
                self.user_table.setCellWidget(row_position, 3, self._create_action_button("Delete", lambda: self.delete_user(user[0])))  # Actions

    def add_user(self):
        """Add a new user"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        email = self.email_input.text().strip()
        role = self.role_combo.currentData()

        if not username or not password or not email:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        result = self.auth_manager.register_user(username=username, password=password, email=email, role=role)

        if result["status"] == "success":
            QMessageBox.information(self, "Success", "User added successfully.")
            self.username_input.clear()
            self.password_input.clear()
            self.email_input.clear()
            self.load_users()
            self.user_updated.emit()
        else:
            QMessageBox.warning(self, "Error", result.get("message", "Failed to add user."))

    def delete_user(self, username: str):
        """Delete a user"""
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete user {username}?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement user deletion in auth_manager
            self.load_users()
            self.user_updated.emit()

    def _create_action_button(self, text: str, callback) -> QPushButton:
        """Create an action button for the table"""
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button