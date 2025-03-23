"""
This module provides the ToolManager class for managing tools with a specific API key.
"""


class ToolManager:
    """
    ToolManager is responsible for managing tools using a provided API key.
    """

    def __init__(self, api_key):
        self.api_key = api_key

    def use_profile(self, profile_name):
        """
        Use a specific scanning profile.

        Parameters:
        profile_name (str): The name of the profile to use.
        """
        print(f"Using profile: {profile_name}")
        # Add your profile usage logic here

    def get_api_key(self):
        """
        Get the API key.

        Returns:
        str: The API key.
        """
        return self.api_key
