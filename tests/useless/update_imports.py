import os
import re
from typing import List, Dict, Optional, Any

# Define the mapping of old import paths to new import paths
import_mapping = {
    "app.": "app.",
    "app.ai.": "app.ai.",
    "app.analytics.": "app.analytics.",
    "app.auth.": "app.auth.",
    "app.code.": "app.code.",
    "app.collaboration.": "app.collaboration.",
    "app.config.": "app.config.",
    "app.core.": "app.core.",
    "app.db.": "app.db.",
    "app.gui.": "app.gui.",
    "app.install.": "app.install.",
    "app.integrations.": "app.integrations.",
    "app.knowledge.": "app.knowledge.",
    "app.logging.": "app.logging.",
    "app.management.": "app.management.",
    "app.middleware.": "app.middleware.",
    "app.models.": "app.models.",
    "app.modules.": "app.modules.",
    "app.notifications.": "app.notifications.",
    "app.optimization.": "app.optimization.",
    "app.project.": "app.project.",
    "app.security.": "app.security.",
    "app.services.": "app.services.",
    "app.settings.": "app.settings.",
    "app.setup.": "app.setup.",
    "app.styles.": "app.styles.",
    "app.tests.": "app.tests.",
    "app.tools.": "app.tools.",
    "app.updates.": "app.updates.",
    "app.utils.": "app.utils.",
}

# Function to update imports in a file
def update_imports_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = content
    for old_import, new_import in import_mapping.items():
        updated_content = re.sub(
            rf"from\s+{re.escape(old_import)}", f"from {new_import}", updated_content
        )
        updated_content = re.sub(
            rf"import\s+{re.escape(old_import)}", f"import {new_import}", updated_content
        )

    # Add missing imports based on code context
    if "List[" in updated_content and "from typing import List" not in updated_content:
        updated_content = "from typing import List\n" + updated_content
    if "Dict[" in updated_content and "from typing import Dict" not in updated_content:
        updated_content = "from typing import Dict\n" + updated_content
    if "Optional[" in updated_content and "from typing import Optional" not in updated_content:
        updated_content = "from typing import Optional\n" + updated_content
    if "Any" in updated_content and "from typing import Any" not in updated_content:
        updated_content = "from typing import Any\n" + updated_content
    if "logger." in updated_content and "import logging" not in updated_content:
        updated_content = "import logging\n" + updated_content

    # Handle custom module imports
    if "services." in updated_content and "from app.services" not in updated_content:
        updated_content = re.sub(
            r"from\s+services\.", "from app.services.", updated_content
        )
    if "tabs." in updated_content and "from app.tabs" not in updated_content:
        updated_content = re.sub(
            r"from\s+tabs\.", "from app.tabs.", updated_content
        )

    # Analyze code context using AST to determine which imports are needed
    def get_used_imports(code):
        import ast
        used_imports = set()
        
        # Define third_party_imports within the function scope
        third_party_imports = {
            "PyQt6": "from PyQt6 import QtWidgets, QtCore",
            "sqlalchemy": "from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime\nfrom sqlalchemy.orm import Session, relationship",
            "requests": "import requests",
            "bs4": "from bs4 import BeautifulSoup",
            "pkg_resources": "import pkg_resources",
            "fpdf": "from fpdf import FPDF",
            "cryptography": "from cryptography.fernet import Fernet",
            "jinja2": "import jinja2",
            "bleach": "import bleach",
            "ssl": "import ssl",
            "argparse": "import argparse",
            "subprocess": "import subprocess",
            "os": "import os",
            "sys": "import sys",
            "json": "import json",
            "re": "import re",
            "typing": "from typing import List, Dict, Optional, Any",
            "pathlib": "from pathlib import Path",
            "shutil": "import shutil",
            "datetime": "from datetime import datetime",
            "aiohttp": "import aiohttp",
            "psycopg2": "import psycopg2",
            "venv": "import venv",
            "ast": "import ast",
            "pylint": "import pylint",
            "radon": "import radon.complexity as radon_complexity\nimport radon.metrics as radon_metrics\nimport radon.visitors as radon_visitors",
            "autopep8": "import autopep8",
        }
        
        try:
            # First attempt to parse the code normally
            try:
                tree = ast.parse(code)
                
                # Track imported names and their usage
                for node in ast.walk(tree):
                    # Handle direct imports
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            used_imports.add(alias.name.split('.')[0])
                    
                    # Handle from ... import statements
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            used_imports.add(node.module.split('.')[0])
                        for alias in node.names:
                            used_imports.add(alias.name)
                    
                    # Handle function calls and attribute access
                    if isinstance(node, ast.Attribute):
                        module = node.value
                        while isinstance(module, ast.Attribute):
                            module = module.value
                        if isinstance(module, ast.Name):
                            used_imports.add(module.id)
                    
                    # Handle variable names
                    if isinstance(node, ast.Name):
                        used_imports.add(node.id)
            
            except SyntaxError as e:
                print(f"Syntax error parsing code: {e}")
                # If normal parsing fails, try parsing with error recovery
                try:
                    # Attempt to parse with error recovery
                    tree = ast.parse(code, mode='exec')
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                used_imports.add(alias.name.split('.')[0])
                        if isinstance(node, ast.ImportFrom):
                            if node.module:
                                used_imports.add(node.module.split('.')[0])
                            for alias in node.names:
                                used_imports.add(alias.name)
                except Exception as e:
                    print(f"Error recovery parsing failed: {e}")
                    # Fall back to simple string matching
                    for lib in third_party_imports.keys():
                        if lib in code:
                            used_imports.add(lib)
        
        except Exception as e:
            print(f"Unexpected error analyzing code: {e}")
            # Fall back to simple string matching
            for lib in third_party_imports.keys():
                if lib in code:
                    used_imports.add(lib)
        
        # Attach the third_party_imports to the function for external access
        get_used_imports.third_party_imports = third_party_imports
        return used_imports

    # Get actually used imports from the code
    used_imports = get_used_imports(updated_content)

    # Handle third-party library imports based on actual usage
    for lib, import_statement in get_used_imports.third_party_imports.items():
        if lib in used_imports and import_statement not in updated_content:
            updated_content = import_statement + "\n" + updated_content

    # Handle custom module imports
    if "codebreaker." in updated_content and "from app.codebreaker" not in updated_content:
        updated_content = re.sub(
            r"from\s+codebreaker\.", "from app.codebreaker.", updated_content
        )
    if "middleware." in updated_content and "from app.middleware" not in updated_content:
        updated_content = re.sub(
            r"from\s+middleware\.", "from app.middleware.", updated_content
        )
    if "analytics_system." in updated_content and "from app.analytics_system" not in updated_content:
        updated_content = re.sub(
            r"from\s+analytics_system\.", "from app.analytics_system.", updated_content
        )

    # Handle standard library imports
    if "ssl." in updated_content and "import ssl" not in updated_content:
        updated_content = "import ssl\n" + updated_content
    if "argparse." in updated_content and "import argparse" not in updated_content:
        updated_content = "import argparse\n" + updated_content
    if "subprocess." in updated_content and "import subprocess极" not in updated_content:
        updated_content = "import subprocess\n" + updated_content

    if updated_content != content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(updated_content)

# Recursively update imports in all Python files in the app directory
for root, _, files in os.walk("app"):
    for file in files:
        if file.endswith(".py"):
            update_imports_in_file(os.path.join(root, file))

print("Import statements updated successfully.")