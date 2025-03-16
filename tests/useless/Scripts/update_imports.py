# update_imports.py
import os
import sys
from pathlib import Path
import re
import logging
from datetime import datetime
import ast
from typing import List, Dict, Set

class ImportUpdater:
    def __init__(self):
        # Get the correct base directory
        self.script_dir = Path(__file__).resolve().parent
        self.base_dir = self.script_dir.parent
        self.backup_dir = self.base_dir / 'backups'
        self.setup_logging()
        
        # Define import mappings
        self.import_mappings = self.get_import_mappings()

    def get_import_mappings(self) -> Dict[str, List[str]]:
        """Get import mappings from actual project structure."""
        mappings = {
            'app.models': [],
            'app.services': [],
            'app.utils': []
        }
        
        # Scan models directory
        models_dir = self.base_dir / 'app' / 'models'
        if models_dir.exists():
            for file in models_dir.glob('*.py'):
                if file.stem != '__init__':
                    mappings['app.models'].append(file.stem)
        
        # Scan services directory
        services_dir = self.base_dir / 'app' / 'services'
        if services_dir.exists():
            for file in services_dir.glob('*.py'):
                if file.stem != '__init__':
                    mappings['app.services'].append(file.stem)
        
        # Add default mappings if directories are empty
        if not mappings['app.models']:
            mappings['app.models'] = [
                'User',
                'Project',
                'Vulnerability',
                'Scan',
                'SecurityEvent',
                'ScanTarget',
                'Base'
            ]
        
        if not mappings['app.services']:
            mappings['app.services'] = [
                'UserService',
                'ProjectService',
                'VulnerabilityService',
                'ScanService',
                'AIService',
                'ReportService',
                'ToolManager'
            ]
        
        return mappings

    def setup_logging(self):
        """Configure logging."""
        log_dir = self.base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'import_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_project_structure(self):
        """Check and create basic project structure if needed."""
        required_dirs = [
            self.base_dir / 'app',
            self.base_dir / 'app' / 'models',
            self.base_dir / 'app' / 'services',
            self.base_dir / 'app' / 'utils',
            self.base_dir / 'tests',
            self.base_dir / 'logs',
            self.base_dir / 'database'
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {directory}")
                
                # Create __init__.py for Python packages
                if 'app' in directory.parts:
                    init_file = directory / '__init__.py'
                    if not init_file.exists():
                        init_file.touch()
                        self.logger.info(f"Created {init_file}")

    def read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding handling."""
        encodings = ['utf-8', 'latin1', 'cp1252', 'ascii']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"Error reading {file_path} with {encoding} encoding: {e}")
                raise
        
        raise UnicodeDecodeError(f"Unable to read {file_path} with any supported encoding")

    def write_file_content(self, file_path: Path, content: str):
        """Write file content with proper encoding."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Error writing to {file_path}: {e}")
            raise

    def backup_file(self, file_path: Path):
        """Create a backup of the file before modifying it."""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{file_path.name}.{timestamp}.bak"
            content = self.read_file_content(file_path)
            self.write_file_content(backup_path, content)
            self.logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            self.logger.error(f"Error creating backup for {file_path}: {e}")
            raise

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        exclude_dirs = {'.git', 'venv', '__pycache__', 'backups', 'migrations'}
        
        for path in self.base_dir.rglob('*.py'):
            if not any(d in path.parts for d in exclude_dirs):
                python_files.append(path)
        
        return sorted(python_files)

    def update_file_imports(self, file_path: Path):
        """Update imports in a single file."""
        try:
            content = self.read_file_content(file_path)
            
            # Look for app.* imports
            import_pattern = re.compile(r'^(?:from|import)\s+app\..*$', re.MULTILINE)
            matches = import_pattern.findall(content)
            
            if not matches:
                self.logger.info(f"No app.* imports found in {file_path}")
                return
            
            # Create backup before modifying
            self.backup_file(file_path)
            
            # Update imports
            new_content = content
            for old_import in matches:
                # Parse the import statement
                if old_import.startswith('from'):
                    module = old_import.split()[1]
                    if module in self.import_mappings:
                        imports = self.import_mappings[module]
                        new_import = f"from {module} import {', '.join(sorted(imports))}"
                        new_content = new_content.replace(old_import, new_import)
            
            if new_content != content:
                self.write_file_content(file_path, new_content)
                self.logger.info(f"Updated imports in {file_path}")
            else:
                self.logger.info(f"No changes needed in {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error updating imports in {file_path}: {e}")
            raise

    def run(self):
        """Run the import update process."""
        try:
            print("\nChecking project structure...")
            self.check_project_structure()
            
            self.logger.info("Starting import updates...")
            
            # Find all Python files
            python_files = self.find_python_files()
            self.logger.info(f"Found {len(python_files)} Python files")
            
            # Update imports in each file
            for file_path in python_files:
                self.logger.info(f"Processing {file_path}")
                try:
                    self.update_file_imports(file_path)
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {e}")
                    continue
            
            self.logger.info("Import updates completed!")
            print("\nImport updates completed!")
            print(f"Backup location: {self.backup_dir}")
            print(f"Logs location: {self.base_dir / 'logs'}")
            
        except Exception as e:
            self.logger.error(f"Import update process failed: {e}")
            print("\nError: Import update process failed!")
            print(f"Check the logs for details: {self.base_dir / 'logs'}")
            sys.exit(1)

if __name__ == "__main__":
    updater = ImportUpdater()
    updater.run()
