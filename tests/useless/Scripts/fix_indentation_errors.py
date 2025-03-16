import re
from pathlib import Path
from backup_utils import create_backup

def fix_indentation(file_path):
    """Fix indentation errors in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        # Remove unexpected indentation
        if re.match(r'^\s+[^\s]', line):
            line = line.lstrip()
        fixed_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

def main():
    project_dir = Path("app")
    files_to_fix = list(project_dir.rglob("*.py"))
    
    # Create backup before making changes
    backup_path = create_backup(files_to_fix, "fix_indentation_errors")
    print(f"Backup created at {backup_path}")
    
    # Apply fixes
    for file_path in files_to_fix:
        print(f"Processing {file_path}")
        fix_indentation(file_path)

if __name__ == "__main__":
    main()
