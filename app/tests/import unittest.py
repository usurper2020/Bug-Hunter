import unittest
from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles

class TestLocalization(unittest.TestCase):

def test_config_localization(self):
config = Config()
self.assert_equal(config.get('LANGUAGE'), 'en')
if __name__ == '__main__':
unittest.main()