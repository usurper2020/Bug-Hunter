from PyQt6 import QtWidgets
from ..services.vulnerability_scanner import VulnerabilityScanner
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

class BugBountyTargetTab(QWidget):
    """
    Tab widget for managing bug bounty targets.

    This widget provides:
    - Input field for adding new targets
    - List of current targets
    - Buttons for managing targets
    - Integration with the vulnerability scanner
    """

    def __init__(self):
        super().__init__()
        self.scanner = VulnerabilityScanner()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()

        # Target input
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target URL or IP address")
        layout.addWidget(self.target_input)

        # Add target button
        add_button = QPushButton("Add Target")
        add_button.clicked.connect(self.add_target)
        layout.addWidget(add_button)

        # Target list
        self.target_list = QListWidget()
        layout.addWidget(QLabel("Current Targets:"))
        layout.addWidget(self.target_list)

        # Scan button
        scan_button = QPushButton("Scan Selected Target")
        scan_button.clicked.connect(self.scan_target)
        layout.addWidget(scan_button)

        self.setLayout(layout)

    def add_target(self):
        """Add a new target to the list."""
        # The line `target = self.target_input.text().strip()` is retrieving the text entered in the
        # QLineEdit widget named `target_input` and removing any leading or trailing whitespace
        # characters using the `strip()` method. This ensures that any extra spaces or newlines are
        # removed from the input before further processing or validation.
        # The line `target = self.target_input.text().strip()` is retrieving the text entered in the
        # QLineEdit widget named `target_input` and removing any leading or trailing whitespace
        # characters using the `strip()` method. This ensures that any extra spaces or newlines are
        # removed from the input before further processing or validation.
        target = self.target_input.text().strip()
        if target and not self.is_target_in_list(target):
            self.target_list.addItem(target)
            self.target_input.clear()

    def is_target_in_list(self, target):
        """Check if the target is already in the list."""
        return target in [self.target_list.item(i).text() for i in range(self.target_list.count())]

    def scan_target(self):
        """Scan the selected target for vulnerabilities."""
        if selected := self.target_list.currentItem():
            target = selected.text()
            results = self.scanner.scan(target)
            self.display_results(results)
        
    def display_results(self, results):
        """Display the scan results in a message box."""
        message_box = QMessageBox()
        message_box.setWindowTitle("Scan Results")
        message_box.setText("\n".join(results) if results else "No vulnerabilities found.")
        message_box.exec()
