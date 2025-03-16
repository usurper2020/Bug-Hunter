from typing import List, Dict, Optional, Any
import re
from typing import Dict
from typing import Any, Dict
from pathlib import Path
import logging

class LoggerConfig:
	"""
	Configuration for logging in the BugHunter application.
	"""
	def __init__(self):
		self.log_dir = Path('logs')
		self.log_dir.mkdir(parents=True, exist_ok=True)
		self.log_level = logging.INFO

	def setup_logging(self):
		"""
		Set up logging configuration for the application.
		"""
		root_logger = logging.getLogger()
		root_logger.setLevel(self.log_level)
		log_file = self.log_dir / 'bughunter.log'
		root_logger.handlers = []
		file_handler = logging.FileHandler(log_file)
		file_handler.setLevel(self.log_level)
		file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
		root_logger.addHandler(file_handler)
		console_handler = logging.StreamHandler()
		console_handler.setLevel(logging.DEBUG)
		console_handler.setFormatter(logging.Formatter('%(message)s'))
		root_logger.addHandler(console_handler)
		self._extracted_from_setup_logging_('security', 'security.log')
		self._extracted_from_setup_logging_('audit', 'audit.log')

	# TODO Rename this here and in `setup_logging`
	def _extracted_from_setup_logging_(self, arg0, arg1):
		security_logger = logging.getLogger(arg0)
		security_file = self.log_dir / arg1
		security_handler = logging.FileHandler(security_file)
		security_handler.setLevel(logging.INFO)
		security_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
		security_logger.addHandler(security_handler)
		security_logger.setLevel(logging.INFO)

	@staticmethod
	def get_logger(name: str) -> logging.Logger:
		"""
		Get a logger instance with the specified name.
		"""
		return logging.getLogger(name)

	@staticmethod
	def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
		"""
		Log a security event.
		"""
		security_logger = logging.getLogger('security')
		security_logger.info(f'Security Event - Type: {event_type} - Details: {details}')

	@staticmethod
	def log_audit_event(user: str, action: str, details: Dict[str, Any]) -> None:
		"""
		Log an audit event.
		"""
		audit_logger = logging.getLogger('audit')
		audit_logger.info(f'Audit Event - User: {user} - Action: {action} - Details: {details}')

	@staticmethod
	def log_error(logger_name: str, error: Exception, context: Dict[str, Any] = None) -> None:
		"""
		Log an error with context.
		"""
		logger = logging.getLogger(logger_name)
		error_details = {'error': str(error), 'context': context}
		logger.error(f'Error occurred: {error_details}', exc_info=True)

# Initialize logging configuration
logger_config = LoggerConfig()
logger_config.setup_logging()
