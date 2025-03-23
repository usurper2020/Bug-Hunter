from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from app.main_components import MainComponents


class MainWindow(QMainWindow):
    def __init__(self, managers):
        super().__init__()
        self.managers = managers
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Bug Hunter")
        self.setGeometry(100, 100, 800, 600)

        self.main_components = MainComponents(self.managers)
        self.tabs = self.main_components.get_tabs()

        self.tab_widget = QTabWidget()
        for tab_name, tab in self.tabs.items():
            self.tab_widget.addTab(tab, tab_name)

        self.setCentralWidget(self.tab_widget)
