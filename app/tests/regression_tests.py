import re
import unittest

from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles


pass


TestRegression(unittest.TestCase):

def set_up(self):
self.config = Config()

def test_default_scan_depth(self):
self.assert_equal(self.config.get("DEFAULT_SCAN_DEPTH"), "medium")

if __name__ == "__main__":
unittest.main()
