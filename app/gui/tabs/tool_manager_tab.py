# app/gui/tabs/tool_management_tab.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
)
from app.integrations.github_manager import GitHubManager


class ToolManagementTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.github_manager = GitHubManager(some_param="example")
        self.load_downloaded_repositories()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.repo_list = QListWidget(self)
        self.layout.addWidget(self.repo_list)

        self.button_layout = QHBoxLayout()

        self.install_button = QPushButton("Install", self)
        self.install_button.clicked.connect(self.install_selected_tool)
        self.button_layout.addWidget(self.install_button)

        self.remove_button = QPushButton("Remove", self)
        self.remove_button.clicked.connect(self.remove_selected_tool)
        self.button_layout.addWidget(self.remove_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def load_downloaded_repositories(self):
        repos = self.github_manager.list_downloaded_repositories()
        self.repo_list.clear()
        for repo in repos:
            self.repo_list.addItem(repo)

    def install_selected_tool(self):
        selected_item = self.repo_list.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self, "Selection Error", "Please select a tool to install."
            )
            return

        repo_name = selected_item.text()
        success = self.github_manager.install_tool(repo_name)
        if success:
            QMessageBox.information(
                self, "Success", f"Tool {repo_name} installed successfully."
            )
        else:
            QMessageBox.critical(self, "Error", f"Failed to install tool {repo_name}.")

    def remove_selected_tool(self):
        selected_item = self.repo_list.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self, "Selection Error", "Please select a tool to remove."
            )
            return

        repo_name = selected_item.text()
        success = self.github_manager.remove_tool(repo_name)
        if success:
            self.repo_list.takeItem(self.repo_list.row(selected_item))
            QMessageBox.information(
                self, "Success", f"Tool {repo_name} removed successfully."
            )
        else:
            QMessageBox.critical(self, "Error", f"Failed to remove tool {repo_name}.")
