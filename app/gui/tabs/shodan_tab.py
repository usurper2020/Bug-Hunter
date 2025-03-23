import re
import os
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QSpinBox,
    QFileDialog,
)
from app.install.integration_manager import ShodanIntegration

"""
Shodan Integration Tab Module.

This module provides the Shodan integration interface for BugHunter,
allowing users to perform security reconnaissance directly from the GUI.

Classes:
ShodanTab: Shodan integration tab class.
"""


class ShodanTab(QWidget):
    """
    Shodan integration tab for BugHunter.

    Attributes:
        target_input (QLineEdit): Input field for target to search.
        search_button (QPushButton): Button to initiate search.
        results_text (QTextEdit): Text area to display search results.
        filter_combo (QComboBox): Dropdown for search filters.
        real_time_checkbox (QCheckBox): Checkbox to enable real-time monitoring.
        api_key_input (QLineEdit): Input field for Shodan API key.
        page_input (QSpinBox): Input field for pagination.
        export_button (QPushButton): Button to export search results.
    """

    def __init__(self):
        """Initialize the Shodan tab."""
        super().__init__()
        self.shodan_client = ShodanIntegration()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """Initialize the user interface components."""
        layout = QVBoxLayout()

        # API Key Section
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("Shodan API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Shodan API key here...")
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

        # Search controls
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Target:"))

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText(
            "Enter target to search (IP, domain, etc.)"
        )
        search_layout.addWidget(self.target_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Open Ports", "Services", "Organizations"])
        search_layout.addWidget(self.filter_combo)

        self.search_button = QPushButton("Search")
        search_layout.addWidget(self.search_button)

        layout.addLayout(search_layout)

        # Real-time monitoring checkbox
        self.real_time_checkbox = QCheckBox("Enable Real-time Monitoring")
        layout.addWidget(self.real_time_checkbox)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(QLabel("Page:"))
        self.page_input = QSpinBox()
        self.page_input.setMinimum(1)
        pagination_layout.addWidget(self.page_input)
        layout.addLayout(pagination_layout)

        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Export button
        self.export_button = QPushButton("Export Results")
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def connect_signals(self):
        """Connect UI signals to appropriate slots."""
        self.search_button.clicked.connect(self.perform_search)
        self.export_button.clicked.connect(self.export_results)

    def perform_search(self):
        """Perform Shodan search and display results."""
        target = self.target_input.text().strip()
        api_key = self.api_key_input.text().strip()
        page = self.page_input.value()

        if not target:
            QMessageBox.warning(self, "Invalid Input", "Please enter a target")
            return

        if not api_key:
            QMessageBox.warning(
                self, "Invalid Input", "Please enter your Shodan API key"
            )
            return

        try:
            filter_option = self.filter_combo.currentText()
            self.shodan_client.set_api_key(api_key)
            results = self.shodan_client.search(target, filter_option, page)
            self.display_results(results)
        except Exception as e:
            QMessageBox.critical(
                self, "Search Error", f"Failed to perform search: {str(e)}"
            )

    def display_results(self, results):
        """Display search results in the text area.

        Args:
            results (dict): Dictionary of search results to display.
        """
        self.results_text.clear()
        if not results.get("results"):
            self.results_text.setText("No results found")
            return

        result_text = "\n\n".join(
            f"IP: {result.get('ip_str', 'N/A')}\n"
            f"Port: {result.get('port', 'N/A')}\n"
            f"Data: {result.get('data', 'N/A')}\n"
            f"Geolocation: {result.get('location', {}).get('city', 'N/A')}, {result.get('location', {}).get('country_name', 'N/A')}\n"
            f"Vulnerabilities: {', '.join(result.get('vulns', []))}"
            for result in results["results"]
        )
        self.results_text.setText(result_text)

        if self.real_time_checkbox.isChecked():
            # Display real-time monitoring status (this is a placeholder, actual implementation may vary)
            self.results_text.append("\n[Real-time Monitoring Enabled]")

    def export_results(self):
        """Export search results to a file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options,
        )
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.results_text.toPlainText())

    def cleanup(self):
        """Clean up resources before closing."""
        self.results_text.clear()
