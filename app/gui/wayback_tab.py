import logging
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QComboBox
)
from app.gui.base_tab import BaseTab
from app.services.wayback_machine_integration import WaybackMachineIntegration

class WaybackMachineException(Exception):
    """Custom exception for Wayback Machine errors"""
    pass


class WaybackTab(BaseTab):
    """
    WaybackTab is a GUI tab for interfacing with the Wayback Machine. It allows users to search for snapshots, page changes, and content analysis of a given URL.
    Attributes:
        wayback (WaybackMachineIntegration): Instance of WaybackMachineIntegration for performing searches.
        logger (logging.Logger): Logger instance for logging messages.
        layout (QVBoxLayout): Main layout of the tab.
        url_input (QLineEdit): Input field for entering the URL to search.
        search_button (QPushButton): Button to initiate the search.
        search_type_combo (QComboBox): Combo box to select the type of search.
        results_display (QTextEdit): Text area to display search results.
        status_label (QLabel): Label to display the current status.
    Methods:
        __init__(self, parent=None, wayback_integration=None): Initializes the WaybackTab with optional parent and wayback_integration.
        _setup_ui(self): Sets up the UI components of the tab.
        _create_search_section(self): Creates the search section of the UI.
        _create_results_section(self): Creates the results section of the UI.
        _create_status_section(self): Creates the status section of the UI.
        _update_status(self, message: str): Updates the status message displayed in the status section.
        _display_results(self, results): Displays the search results in the results section.
        _perform_search(self): Handles the search operation when the search button is clicked.
        refresh(self): Refreshes the tab content, clearing input and results.
    """
    """Wayback Machine interface tab"""

    def __init__(self, parent=None, wayback_integration=None):
        super().__init__(parent=parent)
        self.wayback = wayback_integration or WaybackMachineIntegration()
        self.logger = logging.getLogger(__name__)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components"""
        self._create_search_section()
        self._create_results_section()
        self._create_status_section()
        self._update_status("Wayback integration ready.")

    def _create_search_section(self):
        search_group = QGroupBox("Wayback Search")
        search_layout = QVBoxLayout()
        search_group.setLayout(search_layout)

        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL to search...")

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._perform_search)

        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.search_button)

        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["Snapshots", "Page Changes", "Content Analysis"])

        search_layout.addLayout(input_layout)
        search_layout.addWidget(self.search_type_combo)

        self.layout.addWidget(search_group)

    def _create_results_section(self):
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("Search results will appear here...")
        self.results_display.setAlignment(Qt.AlignmentFlag.AlignTop)
        results_layout.addWidget(self.results_display)

        self.layout.addWidget(results_group)

    def _create_status_section(self):
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)

        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        self.layout.addWidget(status_group)

    def _update_status(self, message: str):
        """Update status message"""
        self.status_label.setText(message)

    def _display_results(self, results):
        """Display search results"""
        self.results_display.clear()
        if isinstance(results, dict):
            for key, value in results.items():
                self.results_display.append(f"<b>{key}:</b> {value}")

    @pyqtSlot()
    def _perform_search(self):
        """Handle Wayback search"""
        url = self.url_input.text().strip()
        if not url:
            self._update_status("Please enter a URL")
            return

        search_type = self.search_type_combo.currentText()
        try:
            self._update_status(f"Performing {search_type}...")
            if search_type == "Snapshots":
                results = self.wayback.get_snapshots(url)
            elif search_type == "Page Changes":
                results = self.wayback.get_page_changes(url)
            else:  # Content Analysis
                results = self.wayback.analyze_content(url)

            self._display_results(results)
            self._update_status(f"{search_type} completed successfully")
        except WaybackMachineException as e:
            self._update_status(f"Error performing search: {str(e)}")
            self.logger.error(f"Error performing search: {str(e)}")

    def refresh(self):
        """Refresh tab content"""
        self.url_input.clear()
        self.results_display.clear()
        self._update_status("Wayback tab refreshed.")

# from app.gui.wayback_tab import WaybackMachineException

class WaybackMachineIntegration:

    def get_snapshots(self, url):
        # Implement the method to get snapshots
        if not url:
            raise WaybackMachineException("URL cannot be empty")
        print(f"Getting snapshots for URL: {url}")
        return {"snapshot1": "http://example.com/snapshot1", "snapshot2": "http://example.com/snapshot2"}

    def get_page_changes(self, url):
        # Implement the method to get page changes
        if not url:
            raise WaybackMachineException("URL cannot be empty")
        print(f"Getting page changes for URL: {url}")
        return {"change1": "Page change result 1", "change2": "Page change result 2"}

    def analyze_content(self, url):
        # Implement the method to analyze content
        print(f"Analyzing content for URL: {url}")
        return {"analysis1": "Content analysis result 1", "analysis2": "Content analysis result 2"}
