from PyQt6.QtWidgets import QWidget, QVBoxLayout
from typing import Optional

"""Base tab implementation for the BugHunter application."""

class BaseTab(QWidget):
	"""
	Base class for all tabs in the BugHunter application.
	def __init__(self, parent: Optional[QWidget] = None):
	This class provides a common interface and basic functionality for all tab widgets in the application.
	It sets up the main layout and provides methods to setup the UI components and connect signals.
	Derived classes should implement the `_setup_ui` and `_connect_signals` methods to define their specific UI and signal connections.
	"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.layout = QVBoxLayout()
		self.setup_ui()
		self._setup_ui()
		self.connect_signals()
	def setup_ui(self):
	def _setup_ui(self):
		"""
		Setup the UI components.
		This method should be overridden by derived classes to define their specific UI components.
		"""
		pass

	def connect_signals(self):
		"""Connect Qt signals"""
		pass

	def refresh(self):
		"""
		Refresh tab content.
		This method should be overridden by derived classes to perform specific refresh operations,
		such as updating displayed data, reloading configurations, or resetting UI elements.
		"""
		pass
