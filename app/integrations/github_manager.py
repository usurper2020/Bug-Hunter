from typing import List, Dict, Optional, Any
import requests
from pathlib import Path
import zipfile
import os
import shutil
import logging
import subprocess
import time
import sys

"""
GitHub Manager for the BugHunter application.

Handles GitHub API interactions and repository management.
"""


class GitHubManager:
    """Manages GitHub API interactions and repository operations."""

    def __init__(self, some_param: Any, api_token: Optional[str] = None):
        self.some_param = some_param
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if api_token:
            self.headers["Authorization"] = f"token {api_token}"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self.downloaded_repos_dir = Path("downloaded_repositories")
        self.downloaded_repos_dir.mkdir(exist_ok=True)

    def search_repositories(self, query: str) -> List[Dict]:
        """
        Search for repositories on GitHub.

        Args:
            query: Search query

        Returns:
            List of dictionaries containing repository information
        """
        url = f"{self.base_url}/search/repositories"
        params = {"q": query}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to search repositories: {e}")
            return []

    def get_repository(self, owner: str, repo: str) -> Optional[Dict]:
        """
        Get repository information from GitHub.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary containing repository information or None if failed
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            self.logger.info(f"Repository {owner}/{repo} retrieved successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve repository {owner}/{repo}: {e}")
            return None

    def download_repository(
        self, owner: str, repo: str, target_dir: Path, retries: int = 3
    ) -> bool:
        """
        Download a GitHub repository.

        Args:
            owner: Repository owner
            repo: Repository name
            target_dir: Directory to save the repository
            retries: Number of retries for the download

        Returns:
            True if download was successful, False otherwise
        """
        url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
        for attempt in range(retries):
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(target_dir / f"{repo}.zip", "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.logger.info(f"Repository {owner}/{repo} downloaded successfully.")
                return True
            except requests.exceptions.RequestException as e:
                self.logger.error(
                    f"Failed to download repository {owner}/{repo} (attempt {attempt + 1}): {e}"
                )
                time.sleep(2**attempt)
        return False

    def extract_repository(self, repo_zip: Path, extract_to: Path) -> bool:
        """
        Extract a downloaded repository.

        Args:
            repo_zip: Path to the downloaded repository zip file
            extract_to: Directory to extract the repository

        Returns:
            True if extraction was successful, False otherwise
        """
        try:
            with zipfile.ZipFile(repo_zip, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            self.logger.info(f"Repository extracted to {extract_to}.")
            return True
        except zipfile.BadZipFile as e:
            self.logger.error(f"Failed to extract repository: {e}")
            return False

    def validate_repository(self, extract_to: Path) -> bool:
        """
        Validate the structure and contents of the extracted repository.

        Args:
            extract_to: Directory where the repository was extracted

        Returns:
            True if validation was successful, False otherwise
        """
        # Placeholder for actual validation logic
        # For now, we will just check if the directory is not empty
        if any(extract_to.iterdir()):
            self.logger.info(f"Repository {extract_to} validated successfully.")
            return True
        else:
            self.logger.error(f"Repository {extract_to} is empty or invalid.")
            return False

    def convert_code_to_python(self, source_dir: Path, target_dir: Path) -> None:
        """
        Convert code to Python and place it in the target directory.

        Args:
            source_dir: Directory containing the source code
            target_dir: Directory to save the converted Python code
        """
        # Placeholder for actual conversion logic
        # For now, we will just copy the files
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
        for item in source_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, target_dir / item.name)
            else:
                shutil.copy2(item, target_dir / item.name)
        self.logger.info(f"Code converted to Python and saved to {target_dir}.")

    def process_repository(self, owner: str, repo: str, target_dir: Path) -> bool:
        """
        Process the repository: download, extract, validate, and convert code.

        Args:
            owner: Repository owner
            repo: Repository name
            target_dir: Directory to save the processed code

        Returns:
            True if processing was successful, False otherwise
        """
        if self.download_repository(owner, repo, target_dir):
            repo_zip = target_dir / f"{repo}.zip"
            extract_to = target_dir / repo
            if self.extract_repository(repo_zip, extract_to):
                if self.validate_repository(extract_to):
                    self.convert_code_to_python(
                        extract_to, target_dir / "converted_code"
                    )
                    self.handle_dependencies(target_dir / "converted_code")
                    self.cleanup(repo_zip, extract_to)
                    self.logger.info(
                        f"Repository {owner}/{repo} processed successfully."
                    )
                    return True
        self.logger.error(f"Failed to process repository {owner}/{repo}.")
        return False

    def handle_dependencies(self, target_dir: Path) -> None:
        """
        Handle dependencies for the converted code.

        Args:
            target_dir: Directory containing the converted code
        """
        requirements_files = ["requirements.txt", "Pipfile", "environment.yml"]
        for req_file in requirements_files:
            req_path = target_dir / req_file
            if req_path.exists():
                try:
                    if req_file == "requirements.txt":
                        subprocess.check_call(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                "-r",
                                str(req_path),
                            ]
                        )
                    elif req_file == "Pipfile":
                        subprocess.check_call(["pipenv", "install"])
                    elif req_file == "environment.yml":
                        subprocess.check_call(
                            ["conda", "env", "update", "--file", str(req_path)]
                        )
                    self.logger.info(
                        f"Dependencies installed from {req_file} for code in {target_dir}."
                    )
                except subprocess.CalledProcessError as e:
                    self.logger.error(
                        f"Failed to install dependencies from {req_file}: {e}"
                    )
                break
        else:
            self.logger.info(f"No dependencies to install for code in {target_dir}.")

    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the GitHubManager with the given settings.

        Args:
            config: Dictionary containing configuration settings
        """
        for key, value in config.items():
            setattr(self, key, value)
        self.logger.info("GitHubManager configured with new settings.")

    def cleanup(self, repo_zip: Path, extract_to: Path) -> None:
        """
        Clean up temporary files after processing.

        Args:
            repo_zip: Path to the downloaded repository zip file
            extract_to: Directory where the repository was extracted
        """
        try:
            if repo_zip.exists():
                repo_zip.unlink()
            if extract_to.exists() and extract_to.is_dir():
                shutil.rmtree(extract_to)
            self.logger.info(f"Cleaned up temporary files for {repo_zip.stem}.")
        except Exception as e:
            self.logger.error(f"Failed to clean up temporary files: {e}")

    def report_progress(self, message: str) -> None:
        """
        Report progress of the current operation.

        Args:
            message: Progress message to log
        """
        self.logger.info(message)

    def list_downloaded_repositories(self) -> List[str]:
        """
        List all downloaded repositories.

        Returns:
            List of repository names
        """
        return [
            repo.name for repo in self.downloaded_repos_dir.iterdir() if repo.is_dir()
        ]

    def install_tool(self, repo_name: str) -> bool:
        """
        Install a tool from a downloaded repository.

        Args:
            repo_name: Name of the repository

        Returns:
            True if installation was successful, False otherwise
        """
        repo_path = self.downloaded_repos_dir / repo_name
        if repo_path.exists() and repo_path.is_dir():
            # Placeholder for actual installation logic
            self.logger.info(f"Tool {repo_name} installed successfully.")
            return True
        else:
            self.logger.error(f"Repository {repo_name} does not exist.")
            return False

    def remove_tool(self, repo_name: str) -> bool:
        """
        Remove a downloaded repository.

        Args:
            repo_name: Name of the repository

        Returns:
            True if removal was successful, False otherwise
        """
        repo_path = self.downloaded_repos_dir / repo_name
        if repo_path.exists() and repo_path.is_dir():
            shutil.rmtree(repo_path)
            self.logger.info(f"Tool {repo_name} removed successfully.")
            return True
        else:
            self.logger.error(f"Repository {repo_name} does not exist.")
            return False
