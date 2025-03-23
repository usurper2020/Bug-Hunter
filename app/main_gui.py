from PyQt5.QtWidgets import QMainWindow

class MainGUI(QMainWindow):
    """Main GUI for the BugHunter application."""

    def __init__(self, managers):
        super().__init__()
        self.managers = managers
        self.setWindowTitle("BugHunter Main GUI")
        self.setGeometry(100, 100, 800, 600)  # Set window size

    def show(self):
        """Show the main GUI."""
        super().show()
