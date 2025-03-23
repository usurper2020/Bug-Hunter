import unittest

from app.main import main, main_components, main_gui, main_window


class TestIntegration(unittest.TestCase):
    def test_app_initialization(self):
        app = BugHunterApp()
        self.assert_is_not_none(app)

        if __name__ == "__main__":
            unittest.main()
