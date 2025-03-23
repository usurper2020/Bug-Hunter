import unittest

from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles


class TestConfiguration(unittest.TestCase):
    def test_config_loading(self):
        config = Config()
        self.assert_is_not_none(config)

        if __name__ == "__main__":
            unittest.main()
