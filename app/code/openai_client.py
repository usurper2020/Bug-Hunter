import json
import os
import requests
import logging

class OpenAIClient:
    """Client for interacting with OpenAI API"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        self.logger = logging.getLogger("BugHunter.OpenAIClient")

    def test_connection(self):
        """Test the API connection"""
        try:
            response = requests.get(f"{self.base_url}/test", headers={"Authorization": f"Bearer {self.api_key}"})
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"OpenAI API test failed: {e}")
            raise

    def generate_code(self, prompt, model="text-davinci-003", **kwargs):
        """Generate code using OpenAI"""
        try:
            payload = {
                "prompt": prompt,
                "model": model,
                **kwargs
            }
            response = requests.post(f"{self.base_url}/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            raise
