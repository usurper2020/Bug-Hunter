:

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from app.auth.simple_auth import SimpleAuth  # Import the SimpleAuth class

class LoginGUI(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.auth_service = SimpleAuth()  # Initialize the SimpleAuth
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("Login", self)
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        register_button = QPushButton("Register", self)
        register_button.clicked.connect(self.handle_register)
        layout.addWidget(register_button)

        self.setLayout(layout)
        self.setWindowTitle("Login / Register")

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.auth_service.login(username, password):  # Use SimpleAuth for validation
            self.on_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

    def handle_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.auth_service.register(username, password):  # Use SimpleAuth for registration
            QMessageBox.information(self, "Success", "Registration successful")
        else:
            QMessageBox.warning(self, "Error", "Registration failed")