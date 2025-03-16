#!/usr/bin/env python3
import subprocess
import sys
import os
import venv
import json
import pkg_resources
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
from datetime import datetime

class DependencyManager:
    def __init__(self):
        self.venv_path = Path('venv')
        self.requirements_path = Path('requirements.txt')
        self.requirements_dev_path = Path('requirements-dev.txt')
        self.constraints_path = Path('constraints.txt')
        self.backup_dir = Path('dependency_backups')
        
        # Setup logging
        self.setup_logging()
        
        # Core dependencies that should be handled carefully
        self.core_dependencies = {
            'click': '>=8.0.0',
            'black': '>=25.1.0',
            'pip': '>=23.0.0',
            'setuptools': '>=65.0.0'
        }
        
        # Known conflicts and their resolutions
        self.known_conflicts = {
            'click': {
                'black': '>=8.0.0',
                'flask': '>=7.1.2',
            },
            'setuptools': {
                'pip': '>=65.0.0',
            }
        }

    def setup_logging(self):
        """Configure logging for the dependency manager."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'dependency_manager_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_python_command(self) -> str:
        """Get the appropriate Python command based on the OS."""
        return "python" if sys.platform == "win32" else "python3"

    def get_activate_command(self) -> str:
        """Get the appropriate activation command based on the OS."""
        if sys.platform == "win32":
            return str(self.venv_path / "Scripts" / "activate")
        return f"source {self.venv_path}/bin/activate"

    def backup_requirements(self):
        """Backup existing requirements files."""
        self.backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for req_file in [self.requirements_path, self.requirements_dev_path]:
            if req_file.exists():
                backup_path = self.backup_dir / f"{req_file.stem}_{timestamp}{req_file.suffix}"
                self.logger.info(f"Backing up {req_file} to {backup_path}")
                req_file.rename(backup_path)

    def create_virtual_environment(self):
        """Create a new virtual environment."""
        try:
            if self.venv_path.exists():
                self.logger.info("Removing existing virtual environment...")
                import shutil
                shutil.rmtree(self.venv_path)
            
            self.logger.info("Creating new virtual environment...")
            venv.create(self.venv_path, with_pip=True)
            self.logger.info("Virtual environment created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating virtual environment: {e}")
            raise

    def run_pip_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run a pip command in the virtual environment."""
        pip_path = str(self.venv_path / "Scripts" / "pip") if sys.platform == "win32" else str(self.venv_path / "bin" / "pip")
        return subprocess.run([pip_path] + command, capture_output=True, text=True, check=False)

    def parse_requirements(self, content: str) -> Dict[str, str]:
        """Parse requirements content into a dictionary of package names and versions."""
        requirements = {}
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle different requirement formats
                if '>=' in line or '<=' in line or '==' in line:
                    name = re.split('[<=>]', line)[0].strip()
                    version = line[len(name):].strip()
                else:
                    name = line
                    version = ''
                requirements[name.lower()] = version
        return requirements

    def resolve_conflicts(self, requirements: Dict[str, str]) -> Dict[str, str]:
        """Resolve known conflicts in requirements."""
        resolved = requirements.copy()
        
        for package, conflicts in self.known_conflicts.items():
            if package in resolved:
                for conflict_pkg, required_version in conflicts.items():
                    if conflict_pkg in resolved:
                        self.logger.info(f"Resolving conflict between {package} and {conflict_pkg}")
                        resolved[conflict_pkg] = required_version
        
        return resolved

    def generate_requirements_file(self, requirements: Dict[str, str], path: Path):
        """Generate a requirements file from a dictionary of requirements."""
        with path.open('w') as f:
            for package, version in requirements.items():
                if version:
                    f.write(f"{package}{version}\n")
                else:
                    f.write(f"{package}\n")

    def install_dependencies(self):
        """Install all dependencies in the correct order."""
        try:
            # Install core dependencies first
            self.logger.info("Installing core dependencies...")
            for package, version in self.core_dependencies.items():
                self.run_pip_command(['install', f'{package}{version}'])

            # Install requirements
            self.logger.info("Installing project dependencies...")
            result = self.run_pip_command(['install', '-r', str(self.requirements_path)])
            if result.returncode != 0:
                self.logger.error(f"Error installing dependencies: {result.stderr}")
                raise Exception("Failed to install dependencies")

            # Install dev requirements if they exist
            if self.requirements_dev_path.exists():
                self.logger.info("Installing development dependencies...")
                result = self.run_pip_command(['install', '-r', str(self.requirements_dev_path)])
                if result.returncode != 0:
                    self.logger.error(f"Error installing dev dependencies: {result.stderr}")
                    raise Exception("Failed to install dev dependencies")

        except Exception as e:
            self.logger.error(f"Error during dependency installation: {e}")
            raise

    def verify_installation(self) -> bool:
        """Verify that all dependencies are installed correctly."""
        try:
            self.logger.info("Verifying installations...")
            result = self.run_pip_command(['list'])
            installed = self.parse_requirements(result.stdout)
            
            # Check core dependencies
            for package, version in self.core_dependencies.items():
                if package not in installed:
                    self.logger.error(f"Core package {package} not installed")
                    return False
            
            # Check all requirements
            with self.requirements_path.open() as f:
                requirements = self.parse_requirements(f.read())
                
            for package in requirements:
                if package not in installed:
                    self.logger.error(f"Required package {package} not installed")
                    return False
            
            self.logger.info("All dependencies verified successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during verification: {e}")
            return False

    def fix_all_dependencies(self):
        """Main method to fix all dependency issues."""
        try:
            self.logger.info("Starting dependency resolution process...")
            
            # Backup existing requirements
            self.backup_requirements()
            
            # Create new virtual environment
            self.create_virtual_environment()
            
            # Read and parse requirements
            if self.requirements_path.exists():
                with self.requirements_path.open() as f:
                    requirements = self.parse_requirements(f.read())
            else:
                requirements = {}
            
            # Add core dependencies
            requirements.update(self.core_dependencies)
            
            # Resolve conflicts
            resolved_requirements = self.resolve_conflicts(requirements)
            
            # Generate new requirements file
            self.generate_requirements_file(resolved_requirements, self.requirements_path)
            
            # Install dependencies
            self.install_dependencies()
            
            # Verify installation
            if self.verify_installation():
                self.logger.info("Dependency resolution completed successfully!")
                self.print_success_message()
            else:
                raise Exception("Dependency verification failed")
                
        except Exception as e:
            self.logger.error(f"Error fixing dependencies: {e}")
            self.print_error_message()
            sys.exit(1)

    def print_success_message(self):
        """Print success message with next steps."""
        print("\n" + "="*50)
        print("Dependency Resolution Successful!")
        print("="*50)
        print("\nTo activate your virtual environment:")
        print(f"Run: {self.get_activate_command()}")
        print("\nNext steps:")
        print("1. Review the generated requirements files")
        print("2. Run your tests to verify everything works")
        print("3. Commit the updated requirements files")
        print("\nCheck the logs for detailed information about the process.")

    def print_error_message(self):
        """Print error message with troubleshooting steps."""
        print("\n" + "="*50)
        print("Error During Dependency Resolution")
        print("="*50)
        print("\nTroubleshooting steps:")
        print("1. Check the logs for detailed error messages")
        print("2. Review your requirements files for conflicts")
        print("3. Try resolving specific packages manually")
        print("4. Consider using alternative package versions")
        print("\nFor manual resolution, activate the virtual environment:")
        print(f"Run: {self.get_activate_command()}")

def main():
    """Main function to run the dependency manager."""
    manager = DependencyManager()
    manager.fix_all_dependencies()

if __name__ == "__main__":
    main()
