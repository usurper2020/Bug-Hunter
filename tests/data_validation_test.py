import unittest

from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles


class TestDataValidation(unittest.TestCase):
    def test_config_data_validation(self):
        config = Config()
        self.assert_is_instance(config.get("DB_PORT"), int)

        if __name__ == "__main__":
            unittest.main()
