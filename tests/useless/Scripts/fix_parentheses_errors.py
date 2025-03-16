import re
from pathlib import Path
from backup_utils import create_backup

def fix_parentheses(file_path):
    """Fix parentheses/brackets errors in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix common mismatches
        content = re.sub(r'\(\s*\)', '()', content)  # Remove spaces in empty parentheses
        content = re.sub(r'\[\s*\]', '[]', content)    # Remove spaces in empty brackets
        content = re.sub(r'\{\s*\}', '{}', content)    # Remove spaces in empty braces
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    project_dir = Path("app")
    files_to_fix = list(project_dir.rglob("*.py"))
    
    # Create backup before making changes
    backup_path = create_backup(files_to_fix, "fix_parentheses_errors")
    print(f"Backup created at {backup_path}")
    
    # Apply fixes
    for file_path in files_to_fix:
        print(f"Processing {file_path}")
        fix_parentheses(file_path)

if __name__ == "__main__":
    main()
