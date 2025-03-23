from app.services.simple_auth import SimpleAuth
from app.services.reset_password import ResetPasswordDialog
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)
from dataclasses import dataclass

class LoginDialog(QDialog):
    def __init__(self, _auth_manager=None, _parent=None):
        super().__init__(_parent)
        self.auth_manager = _auth_manager or SimpleAuth()
        self.user_token = None
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 300, 150)  # x, y, width, height
        layout = QVBoxLayout()
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # Password input
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Forgot Password button
        self.forgot_password_button = QPushButton("Forgot Password")
        self.forgot_password_button.clicked.connect(self.open_reset_password_dialog)
        layout.addWidget(self.forgot_password_button)

        self.setLayout(layout)

    def handle_login(self):
        try:
            if self.auth_manager.authenticate(self.username_input.text(), self.password_input.text()):
                QMessageBox.information(self, "Success", "Login successful!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def open_reset_password_dialog(self):
        reset_dialog = ResetPasswordDialog(self.auth_manager, self)
        reset_dialog.exec()
