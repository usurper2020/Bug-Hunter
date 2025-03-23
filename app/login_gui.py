from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from fastapi import HTTPException
from app.auth.auth_service import AuthService  # Updated import path to absolute
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class LoginGUI(QDialog):
    """Login dialog for the BugHunter application."""

    def __init__(self, on_login_success, auth_service: AuthService):
        super().__init__()
        self.on_login_success = on_login_success
        self.auth_service = auth_service
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)  # Set window size

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title label
        title_label = QLabel("Welcome to BugHunter")
        title_label.setFont(QFont("Arial", 16))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.open_registration)
        self.layout.addWidget(self.register_button)

        # Set layout margins and spacing
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

    def login(self):
        """Handle login logic."""
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            # Authenticate user
            if self.auth_service.authenticate_user(username, password):
                self.on_login_success()
                self.close()
            else:
                print("Login failed: Invalid credentials")
        except HTTPException as e:
            print(f"Login failed: {e.detail}")

    def open_registration(self):
        """Open the registration dialog."""
        registration_dialog = RegistrationGUI(self.auth_service)
        registration_dialog.exec_()

class RegistrationGUI(QDialog):
    """Registration dialog for the BugHunter application."""

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Register")
        self.setGeometry(100, 100, 400, 400)  # Set window size

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.layout.addWidget(self.name_input)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.layout.addWidget(self.email_input)

        # Job title input
        self.job_title_input = QLineEdit()
        self.job_title_input.setPlaceholderText("Job Title")
        self.layout.addWidget(self.job_title_input)

        # Phone number input
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number")
        self.layout.addWidget(self.phone_input)

        # Address input
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Street Address")
        self.layout.addWidget(self.address_input)

        # City input
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("City")
        self.layout.addWidget(self.city_input)

        # State input
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText("State")
        self.layout.addWidget(self.state_input)

        # Zip code input
        self.zip_input = QLineEdit()
        self.zip_input.setPlaceholderText("Zip Code")
        self.layout.addWidget(self.zip_input)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

    def register(self):
        """Handle registration logic."""
        name = self.name_input.text()
        email = self.email_input.text()
        job_title = self.job_title_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()
        city = self.city_input.text()
        state = self.state_input.text()
        zip_code = self.zip_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            user = self.auth_service.register_user(username, password, email=email, name=name, job_title=job_title, phone=phone, address=address, city=city, state=state, zip_code=zip_code)
            # Optionally, show a success message or close the dialog
            self.close()
        except HTTPException as e:
            # Handle registration errors (e.g., show a message box)
            print(f"Registration failed: {e.detail}")

if __name__ == "__main__":
    import sys
    # Create a database engine
    engine = create_engine('sqlite:///path_to_your_database.db')  # Update with your database path
    Session = sessionmaker(bind=engine)
    db_session = Session()

    app = QApplication(sys.argv)
    auth_service = AuthService(db=db_session)  # Pass the database session
    window = LoginGUI(on_login_success=lambda: print("Login successful!"), auth_service=auth_service)
    window.show()
    print("Login GUI should now be displayed.")
    sys.exit(app.exec_())