import unittest

from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles


class TestSanity(unittest.TestCase):
    def test_basic_config(self):
        config = Config()
        self.assert_equal(config.get("DB_HOST"), "localhost")

        if __name__ == "__main__":
            unittest.main()
