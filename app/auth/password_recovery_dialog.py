import re
from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

class PasswordRecoveryDialog(QDialog):
    """Dialog for password recovery"""

    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Password Recovery")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Username
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # Security Answer
        self.security_answer_label = QLabel("Security Answer:")
        self.security_answer_input = QLineEdit()
        layout.addWidget(self.security_answer_label)
        layout.addWidget(self.security_answer_input)

        # Recover Button
        self.recover_button = QPushButton("Recover Password")
        self.recover_button.clicked.connect(self.attempt_recovery)
        layout.addWidget(self.recover_button)

        self.setLayout(layout)

    def attempt_recovery(self):
        username = self.username_input.text()
        security_answer = self.security_answer_input.text()

        if not username or not security_answer:
            QMessageBox.warning(self, "Recovery Failed", "All fields are required")
            return

        if self.auth_service.recover_password(username, security_answer):
            QMessageBox.information(self, "Recovery Success", "You can now reset your password.")
            self.accept()  # Close the dialog
        else:
            QMessageBox.warning(self, "Recovery Failed", "Incorrect security answer.")
