# The code defines classes for integrating with external services like Shodan and Wayback Machine, and
# an IntegrationManager class to manage and perform scans using these integrations.
# Add project root to Python path
import sys
from pathlib import Path
import shodan  # Ensure you have the shodan library installed

try:
    import waybackpy  # Ensure you have the waybackpy library installed
except ImportError:
    print(
        "waybackpy library is not installed. Please install it using 'pip install waybackpy'"
    )
    sys.exit(1)
project_root = (
    str(Path(__file__).resolve().parent.parent.parent)
    if "__file__" in globals()
    else str(Path().resolve().parent.parent.parent)
)
# The `sys` module in Python provides access to some variables used or
# maintained by the interpreter and to functions that interact with the
# interpreter. In this specific code snippet, `sys` is being used to manipulate
# the Python path by adding the project root directory to it. This allows the
# code to import modules from directories outside the current working
# directory.
if project_root not in sys.path:
    sys.path.append(project_root)


class WaybackMachineIntegration:
    def get_status(self):
        return "active"

    def get_snapshots(self, target):
        return f"Snapshots for {target}"


import shodan

class ShodanIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = shodan.Shodan(api_key)

    def get_status(self):
        return "active"

    def search(self, target, filter_option, page):
        try:
            results = self.client.search(target, page=page)
            return results
        except shodan.APIError as e:
            raise Exception(f"Shodan API error: {str(e)}")



class IntegrationManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.shodan = ShodanIntegration()
        self.wayback = WaybackMachineIntegration()
        self.initialized = False

    def initialize_integrations(self):
        """Initialize all external service integrations"""
        self.initialized = True

    def get_integration_status(self, target):
        """
        Get the status of all integrations for a given target.
        Args:
            target (str): The target for which to get the integration status.
        Returns:
            dict: A dictionary containing the status of the integrations with the following keys:
                - "initialized" (bool): Whether the integration manager is initialized.
                - "status" (str): "running" if initialized, otherwise "not initialized".
                - "shodan" (str): The status of the Shodan integration, or "unknown" if the status cannot be determined.
                - "wayback" (str): The status of the Wayback integration, or "unknown" if the status cannot be determined.
        Raises:
            ValueError: If the target is None or an empty string.
        """
        if not target:
            raise ValueError("Target cannot be None or empty")

        return {
            "initialized": self.initialized,
            "status": "running" if self.initialized else "not initialized",
            "shodan": self.shodan.get_status()
            if hasattr(self.shodan, "get_status")
            else "unknown",
            "wayback": self.wayback.get_status()
            if hasattr(self.wayback, "get_status")
            else "unknown",
        }

    def perform_integrated_scan(self, target):
        """Perform a scan using all available integrations"""
        if not self.initialized:
            raise RuntimeError("Integration manager not initialized")
        if not target:
            raise ValueError("Target cannot be None or empty")

        return {
            "target": target,
            "shodan_results": self.shodan.search(target)
            if hasattr(self.shodan, "search")
            else None,
            "wayback_results": self.wayback.get_snapshots(target)
            if hasattr(self.wayback, "get_snapshots")
            else None,
        }


if __name__ == "__main__":
    manager = IntegrationManager()
    manager.initialize_integrations()
    target = "example.com"
    print(manager.get_integration_status(target))
    print(manager.perform_integrated_scan(target))
