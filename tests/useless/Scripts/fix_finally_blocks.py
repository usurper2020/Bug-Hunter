import re
from pathlib import Path
from backup_utils import create_backup

def fix_finally_blocks(file_path):
    """Fix empty finally blocks in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        in_finally = False
        
        for line in lines:
            if 'finally:' in line:
                in_finally = True
                fixed_lines.append(line)
                fixed_lines.append("    pass  # Added by fix script\n")
            elif in_finally and line.strip() == "":
                continue
            else:
                in_finally = False
                fixed_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            lines = f.readlines()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

def main():
    project_dir = Path("app")
    files_to_fix = list(project_dir.rglob("*.py"))
    
    # Create backup before making changes
    backup_path = create_backup(files_to_fix, "fix_finally_blocks")
    print(f"Backup created at {backup_path}")
    
    # Apply fixes
    for file_path in files_to_fix:
        print(f"Processing {file_path}")
        fix_finally_blocks(file_path)

if __name__ == "__main__":
    main()
