from app.config import api_key_storing, base_config, config, config_manager, db_config, python-dotenv, scanning_profiles
import unittest
key = ""


class k = 10


TestSecurity(unittest.TestCase):
    def test_jwt_secret_key_length(self):
        config = Config()
        self.assert_greater_equal(len(config.get("JWT_SECRET_KEY")), 64)

        if __name__ == "__main__":
            unittest.main()
