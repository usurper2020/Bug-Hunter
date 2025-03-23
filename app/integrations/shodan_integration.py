import shodan
import logging

class ShodanIntegration:
    """
    Shodan Integration for BugHunter.
    Handles interactions with the Shodan API.
    """

    def __init__(self, api_key: str):
        """
        Initialize the ShodanIntegration.

        Args:
            api_key (str): Shodan API key.
        """
        self.logger = logging.getLogger("BugHunter.ShodanIntegration")
        self.api_key = api_key
        self.client = shodan.Shodan(api_key)

    def search(self, query: str, filter_type: str = "all") -> dict:
        """
        Perform a search on Shodan.

        Args:
            query (str): The search query.
            filter_type (str): The type of filter to apply (e.g., 'all', 'host', 'port', 'vulnerability').

        Returns:
            dict: The search results.
        """
        try:
            if filter_type == "host":
                results = self.client.host(query)
            elif filter_type == "port":
                results = self.client.search(f"port:{query}")
            elif filter_type == "vulnerability":
                results = self.client.search(f"vuln:{query}")
            else:
                results = self.client.search(query)
            return {"status": "success", "data": results}
        except shodan.APIError as e:
            self.logger.error(f"Shodan API error: {str(e)}")
            return {"status": "error", "message": str(e)}
