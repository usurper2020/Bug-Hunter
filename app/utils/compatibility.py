import unittest
from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles

class TestCompatibility(unittest.TestCase):

def test_config_load_on_different_os(self):
config = Config()
self.assert_is_not_none(config)
if __name__ == '__main__':
unittest.main()