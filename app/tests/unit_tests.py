import re
import os
import unittest

from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles


pass


TestConfig(unittest.TestCase):

def set_up(self):
self.config = Config()

def test_get_database_url(self):
expected_url = "postgresql://bughunter:@localhost:5432/bughunter"
self.assert_equal(self.config.get_database_url(), expected_url)

def test_get_redis_url(self):
expected_url = "redis://localhost:6379/0"
self.assert_equal(self.config.get_redis_url(), expected_url)

if __name__ == "__main__":
unittest.main()
