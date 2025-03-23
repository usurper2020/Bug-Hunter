# app/gui/tabs/github_search_tab.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
)
from app.integrations.github_manager import GitHubManager
from pathlib import Path


class GitHubSearchTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.github_manager = GitHubManager(some_param="example")

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Enter repository name...")
        self.layout.addWidget(self.search_bar)

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search_repositories)
        self.layout.addWidget(self.search_button)

        self.results_list = QListWidget(self)
        self.layout.addWidget(self.results_list)

        self.download_button = QPushButton("Download Selected", self)
        self.download_button.clicked.connect(self.download_selected_repository)
        self.layout.addWidget(self.download_button)

        self.setLayout(self.layout)

    def search_repositories(self):
        query = self.search_bar.text()
        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a repository name.")
            return

        # Perform search using GitHubManager
        results = self.github_manager.search_repositories(query)
        self.results_list.clear()
        for repo in results:
            self.results_list.addItem(f"{repo['full_name']}")

    def download_selected_repository(self):
        selected_item = self.results_list.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self, "Selection Error", "Please select a repository to download."
            )
            return

        repo_full_name = selected_item.text()
        owner, repo = repo_full_name.split("/")
        target_dir = Path("downloaded_repositories")

        success = self.github_manager.process_repository(owner, repo, target_dir)
        if success:
            QMessageBox.information(
                self,
                "Success",
                f"Repository {repo_full_name} downloaded and processed successfully.",
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to download and process repository {repo_full_name}.",
            )
