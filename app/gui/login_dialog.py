from app.services.simple_auth import SimpleAuth  # Changed from relative import
from app.gui.registration_dialog import RegistrationDialog  # Ensure the correct import path
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QApplication,
)

import logging
from datetime import datetime, timedelta
class LoginDialog(QDialog):
    WINDOW_TITLE = "BugHunter Login"
    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 200

    def __init__(self, auth_service: SimpleAuth, parent=None):
        """
        Initialize the LoginDialog.

        :param auth_service: An instance of SimpleAuth for handling authentication.
        :param parent: The parent widget of this dialog. Defaults to None.
        """
        super().__init__(parent)
        self.auth_service = auth_service
        self.last_failed_attempt_time = datetime.min
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the user interface for the login dialog.
        """
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        layout = QVBoxLayout()
        self.setup_username_input(layout)
        self.setup_password_input(layout)
        self.setup_buttons(layout)
        self.setLayout(layout)

    def setup_username_input(self, layout):
        """
        Sets up the username input fields.
        """
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

    def setup_password_input(self, layout):
        """
        Sets up the password input fields.
        """
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

    def setup_buttons(self, layout):
        """
        Sets up the login and register buttons.
        """
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.show_registration)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

    def show_registration(self):
        """
        Displays the registration dialog to the user.
        """
        registration_dialog = RegistrationDialog(self.auth_service, self)
        registration_dialog.exec()  # Show the registration dialog

    def attempt_login(self):
        """
        Attempts to log in the user with the provided username and password.
        """
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            if datetime.now() - self.last_failed_attempt_time < timedelta(seconds=5):
                raise ValueError("Too many failed attempts. Please wait before trying again.")
            if not self.auth_service.authenticate(username, password):
                self.last_failed_attempt_time = datetime.now()
                raise ValueError("Invalid username or password.")
            QMessageBox.information(self, "Success", "Login successful!")
            logging.info("User '%s' logged in successfully.", username)
            self.last_failed_attempt_time = datetime.min
        except ValueError as e:
            self.handle_invalid_login(username, str(e))

def handle_invalid_login(self, username, error_message="Invalid username or password."):
    """
    Handles invalid login attempts by logging the error and notifying the user.

    :param username: The username used in the login attempt.
    :param error_message: The error message to display to the user.
    """
    self.password_input.clear()
    QMessageBox.critical(self, "Error", error_message)
    logging.error("Login failed for user '%s': %s", username, error_message)
                
def main():
    import sys
    app = QApplication(sys.argv)
    auth_service = SimpleAuth()  # Assuming SimpleAuth can be instantiated like this
    login_dialog = LoginDialog(auth_service)
    login_dialog.show()  # Change exec() to show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
