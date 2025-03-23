import unittest
from PyQt6.QtWidgets import QApplication
from app.auth.login_dialog import LoginDialog
from unittest.mock import MagicMock

class TestLoginDialog(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.auth_manager = MagicMock()
        self.dialog = LoginDialog(self.auth_manager)

    def test_successful_login(self):
        self.auth_manager.authenticate_user.return_value = {"token": "test_token"}
        self.dialog.username_input.setText("testuser")
        self.dialog.password_input.setText("password123")
        
        self.dialog.handle_login()
        
        self.assertTrue(self.dialog.result() == 1)  # Check if dialog accepted

    def test_failed_login(self):
        self.auth_manager.authenticate_user.return_value = None
        self.dialog.username_input.setText("wronguser")
        self.dialog.password_input.setText("wrongpassword")
        
        self.dialog.handle_login()
        
        self.assertTrue(self.dialog.result() == 0)  # Check if dialog rejected

if __name__ == "__main__":
    unittest.main()
