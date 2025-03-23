import unittest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
from app.auth.registration_dialog import RegistrationDialog

class TestRegistrationDialog(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.auth_service = MagicMock()
        self.dialog = RegistrationDialog(self.auth_service)

    def test_successful_registration(self):
        self.dialog.username_input.setText("testuser")
        self.dialog.password_input.setText("password123")
        self.dialog.confirm_password_input.setText("password123")
        self.dialog.email_input.setText("testuser@example.com")

        self.auth_service.register_user.return_value = True
        self.dialog.attempt_registration()

        self.assertTrue(self.dialog.isAccepted())

    def test_empty_fields(self):
        self.dialog.username_input.setText("")
        self.dialog.password_input.setText("")
        self.dialog.confirm_password_input.setText("")
        self.dialog.email_input.setText("")

        self.dialog.attempt_registration()

        self.assertFalse(self.dialog.isAccepted())

    def test_password_mismatch(self):
        self.dialog.username_input.setText("testuser")
        self.dialog.password_input.setText("password123")
        self.dialog.confirm_password_input.setText("differentpassword")
        self.dialog.email_input.setText("testuser@example.com")

        self.dialog.attempt_registration()

        self.assertFalse(self.dialog.isAccepted())

    def tearDown(self):
        self.dialog.close()

if __name__ == "__main__":
    unittest.main()