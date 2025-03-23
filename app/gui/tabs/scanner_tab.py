import asyncio
from PyQt6 import QtWidgets, QtCore
from app.services.vulnerability_scanner import VulnerabilityScanner
from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
)
import logging

logger = logging.getLogger(__name__)

"""
Scanner Tab Module

This module implements the ScannerTab class, which provides the user interface
for executing security scans within the BugHunter application. The tab allows
users to:
- Select from predefined scan profiles
- Input target URLs or IP addresses
- Execute scans with selected profiles
- View detailed scan results

The tab integrates with the VulnerabilityScanner service to perform actual
scan operations and display results in real-time.
"""


class ScannerTab(QWidget):
    """Provides a comprehensive interface for security scanning operations.

    The ScannerTab widget offers a complete workflow for vulnerability scanning,
    including target selection, profile configuration, scan execution, and
    results visualization. It serves as the primary interface for users to
    interact with the BugHunter scanning capabilities.

    Attributes:
        profile_selector (QComboBox): Dropdown for selecting scan profiles
        target_input (QTextEdit): Field for entering scan targets
        results_display (QTextEdit): Area for displaying scan results
        scanner (VulnerabilityScanner): Service for executing scans
        progress_bar (QProgressBar): Progress bar for scan progress
    """

    def __init__(self):
        super().__init__()
        self.scanner = VulnerabilityScanner()  # Initialize scanner first
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()

        # Scan profile selection
        self.profile_selector = QComboBox()
        self.profile_selector.addItems(self.scanner.get_profiles())
        layout.addWidget(QLabel("Select Scan Profile:"))
        layout.addWidget(self.profile_selector)

        # Target input
        self.target_input = QTextEdit()
        self.target_input.setPlaceholderText("Enter target URLs (one per line)")
        layout.addWidget(self.target_input)

        # Scan button
        self.scan_button = QPushButton("Run Scan")
        self.scan_button.clicked.connect(self.run_scan)
        layout.addWidget(self.scan_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(QLabel("Scan Results:"))
        layout.addWidget(self.results_display)

        self.setLayout(layout)

    async def run_scan_async(self, profile, targets):
        """Run a security scan asynchronously on the specified targets."""
        try:
            self.scan_button.setEnabled(False)
            self.results_display.setPlainText("Scanning in progress...")
            self.progress_bar.setValue(0)
            total_targets = len(targets)
            results = []

            for i, target in enumerate(targets):
                result = await asyncio.to_thread(self.scanner.scan, [target], profile)
                results.append(result)
                self.progress_bar.setValue((i + 1) / total_targets * 100)
                self.results_display.append(f"Results for {target}:\n{result}\n")

            self.results_display.append("Scanning completed.")
        except Exception as e:
            logger.error(f"Scan failed: {str(e)}")
            self.results_display.setPlainText(f"Scan failed: {str(e)}")
        finally:
            self.scan_button.setEnabled(True)

    def run_scan(self):
        """Run a security scan on the specified targets."""
        profile = self.profile_selector.currentText()
        targets = self.target_input.toPlainText().strip().split("\n")
        if targets:
            asyncio.create_task(self.run_scan_async(profile, targets))
        else:
            self.results_display.setPlainText("Please enter at least one target URL.")
