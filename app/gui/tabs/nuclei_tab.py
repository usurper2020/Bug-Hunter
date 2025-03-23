from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from app.services.nuclei_analyzer import NucleiAnalyzer
from app.logging.log_manager import LogManager

class NucleiTab(QWidget):
    """
    Tab widget for Nuclei scanning functionality.

    This widget provides:
    - Input field for target URLs
    - Button to run Nuclei scans
    - Output display for scan results
    - Template management
    """

    def __init__(self):
        super().__init__()
        self.logger = LogManager.get_logger("NucleiTab")
        self.analyzer = NucleiAnalyzer()
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI components."""
        layout = QVBoxLayout()

        # Target input
        self.target_input = self.create_target_input()
        layout.addWidget(self.target_input)

        # Scan button
        scan_button = self.create_scan_button()
        layout.addWidget(scan_button)

        # Results display
        self.results_display = self.create_results_display()
        layout.addWidget(QLabel("Scan Results:"))
        layout.addWidget(self.results_display)

        self.setLayout(layout)

    def create_target_input(self) -> QTextEdit:
        """Create the target input field."""
        target_input = QTextEdit()
        target_input.setPlaceholderText("Enter target URLs (one per line)")
        return target_input

    def create_scan_button(self) -> QPushButton:
        """Create the scan button."""
        scan_button = QPushButton("Run Nuclei Scan")
        scan_button.clicked.connect(self.run_scan)
        return scan_button

    def create_results_display(self) -> QTextEdit:
        """Create the results display field."""
        results_display = QTextEdit()
        results_display.setReadOnly(True)
        return results_display

    def run_scan(self) -> None:
        """Run a Nuclei scan on the specified targets."""
        targets = self.target_input.toPlainText().strip().split("\n")
        if targets:
            try:
                self.logger.info(f"Running Nuclei scan on targets: {targets}")
                results = self.analyzer.scan(targets)
                self.results_display.setPlainText("\n".join(results))
                self.logger.info("Nuclei scan completed successfully.")
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                self.results_display.setPlainText(error_message)
                self.logger.error(error_message)