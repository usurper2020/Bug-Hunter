import re
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

pass
"""Check if .env file exists and contains required variables"""
logger = logging.getLogger(__name__)
env_path = Path('.env')
if not env_path.exists():
logger.error('.env file not found')
create_env_file()
return False
load_dotenv(override=True)
required_vars = ['OPENAI_API_KEY']
missing_vars = []
for var in required_vars:
if not os.getenv(var):
missing_vars.append(var)
if missing_vars:
logger.error(f'Missing environment variables: {', '.join(missing_vars)}')
return False
return True
def create_env_file():
"""Create a template .env file"""
template = '''# OpenAI API Key (Required)
OPENAI_API_KEY=your_api_key_here
# GitHub Token (Optional)
GITHUB_TOKEN=your_github_token_here
'''
try:
with open('.env', 'w') as f:
f.write(template)
logging.info('Created template .env file')
except Exception as e:
logging.error(f'Failed to create .env file: {e}')
template = """# OpenAI API Key (Required)
OPENAI_API_KEY=your_api_key_here

# GitHub Token (Optional)
GITHUB_TOKEN=your_github_token_here
"""

try:
pass
pass
with open(".env", "w") as f:
f.write(template)
logging.info("Created template .env file")
except Exception as e:
logging.error(f"Failed to create .env file: {e}")
