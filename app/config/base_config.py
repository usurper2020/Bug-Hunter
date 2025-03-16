from typing import List, Dict, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Session, relationship
from typing import Any
from typing import Dict
from typing import TYPE_CHECKING, Any, Dict
from pathlib import Path
import os

class BaseConfig:
"""Base configuration class for the BugHunter application."""
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / 'src'
TESTS_DIR = BASE_DIR / 'tests'
UTILS_DIR = BASE_DIR / 'utils'
DATABASE = {'driver': 'sqlite', 'name': 'bughunter.db', 'path': str(BASE_DIR / 'data')}
LOGGING = {'version': 1, 'disable_existing_loggers': False, 'formatters': {'standard': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'}}, 'handlers': {'default': {'level': 'INFO', 'formatter': 'standard', 'class': 'logging.StreamHandler'}, 'file': {'level': 'INFO', 'formatter': 'standard', 'class': 'logging.FileHandler', 'filename': str(BASE_DIR / 'logs' / 'bughunter.log'), 'filename': str(BASE_DIR / 'logs' / 'bughunter.log')}}, 'loggers': {'': {'handlers': ['default', 'file'], 'level': 'INFO', 'propagate': True}}}
AI_CONFIG = {'model_path': str(BASE_DIR / 'models'), 'max_tokens': 1000, 'temperature': 0.7}
TEST_CONFIG = {'test_data_path': str(TESTS_DIR / 'data'), 'mock_responses': str(TESTS_DIR / 'mock_responses')}
SECURITY = {'secret_key': os.getenv('SECRET_KEY', 'default_secret_key'), 'algorithm': 'HS256', 'access_token_expire_minutes': 30}
API = {'version': 'v1', 'prefix': '/api'}
CACHE = {'type': 'redis', 'host': 'localhost', 'port': 6379, 'db': 0}
EMAIL = {'smtp_server': 'smtp.example.com', 'smtp_port': 587, 'smtp_username': os.getenv('SMTP_USERNAME', 'user@example.com'), 'smtp_password': os.getenv('SMTP_PASSWORD', 'password'), 'from_email': 'noreply@example.com'}
FEATURES = {'enable_feature_x': True, 'enable_feature_y': False}
SPACY = {'model': 'en_core_web_sm'}

@classmethod
def get_db_url(cls) -> str:
"""Generate database URL from configuration."""
return f"{cls.DATABASE['driver']}:///{Path(cls.DATABASE['path']) / cls.DATABASE['name']}"

@classmethod
def ensure_directories(cls) -> None:
"""Ensure all required directories exist."""
directories = [cls.DATABASE['path'], os.path.dirname(cls.LOGGING['handlers']['file']['filename']), cls.AI_CONFIG['model_path'], cls.TEST_CONFIG['test_data_path'], cls.TEST_CONFIG['mock_responses']]
for directory in directories:
Path(directory).mkdir(parents=True, exist_ok=True)

@classmethod
def get_config_value(cls, key: str, default: Any=None) -> Any:
"""Safely get configuration value."""
return getattr(cls, key, default)

@classmethod
def update_config(cls, updates: Dict[str, Any]) -> None:
"""Update configuration values."""
for key, value in updates.items():
if hasattr(cls, key):
setattr(cls, key, value)

@classmethod
def get_alembic_config(cls) -> Dict[str, Any]:
"""Get Alembic-specific configuration."""
return {'script_location': 'alembic', 'sqlalchemy.url': cls.get_db_url(), 'file_template': '%%(year)d%%(month).2d%%(day).2d_%%(rev)s_%%(slug)s'}