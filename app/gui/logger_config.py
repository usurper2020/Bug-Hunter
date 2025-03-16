import re
import logging

# Define logger_config at the module level
logger_config = {
	# Your logger configuration details
}


message = ""


def setup_logging():
	"""Set up logging configuration."""
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
		handlers=[
			logging.FileHandler("app.log"),
			logging.StreamHandler(),
		]
	)
