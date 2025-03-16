import re
import logging
from pathlib import Path
from backup_utils import create_backup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("fix_all_errors.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def fix_indentation(file_content):
    """Fix indentation issues in file content"""
    logger.info("Fixing indentation")
    lines = file_content.splitlines()
    fixed_lines = []
    indent_level = 0
    control_structures = ["if", "else", "elif", "for", "while", "try", "except", "finally", "with", "def", "class"]
    block_end_keywords = ["return", "break", "continue", "pass", "raise"]
    dedent_keywords = ["except", "finally", "else", "elif"]
    indent_stack = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        current_indent = len(line) - len(line.lstrip())
        
        # Handle dedent keywords
        if any(stripped.startswith(keyword) for keyword in dedent_keywords):
            if indent_stack:
                indent_level = indent_stack.pop()
            else:
                indent_level = max(0, indent_level - 1)
        
        # Handle control structures
        if any(stripped.startswith(keyword) for keyword in control_structures):
            fixed_lines.append(" " * (indent_level * 4) + stripped)
            indent_stack.append(indent_level)
            indent_level += 1
        elif any(stripped.startswith(keyword) for keyword in block_end_keywords):
            fixed_lines.append(" " * (indent_level * 4) + stripped)
            if indent_stack:
                indent_level = indent_stack.pop()
            else:
                indent_level = max(0, indent_level - 1)
        elif stripped and current_indent != indent_level * 4:
            fixed_lines.append(" " * (indent_level * 4) + stripped)
        elif not stripped:
            fixed_lines.append("")
            if indent_stack:
                indent_level = indent_stack.pop()
            else:
                indent_level = max(0, indent_level - 1)
        else:
            fixed_lines.append(line)
    
    return "\n".join(fixed_lines)

def fix_parentheses(file_content):
    """Fix parentheses/brackets errors in file content"""
    logger.info("Fixing parentheses")
    # Fix common mismatches
    file_content = re.sub(r'\(\s*\)', '()', file_content)  # Remove spaces in empty parentheses
    file_content = re.sub(r'\[\s*\]', '[]', file_content)    # Remove spaces in empty brackets
    file_content = re.sub(r'\{\s*\}', '{}', file_content)    # Remove spaces in empty braces
    
    # Enhanced print statement fixing
    file_content = re.sub(r'\bprint\s+([^\n]+?)(?=\s*(?:#|$))', r'print(\1)', file_content)
    
    # Enhanced unmatched parentheses handling
    stack = []
    for i, char in enumerate(file_content):
        if char in "({[":
            stack.append((char, i))
        elif char in ")}]":
            if not stack or not is_matching_pair(stack[-1][0], char):
                # Remove unmatched closing character
                logger.debug(f"Removing unmatched closing character at position {i}")
                file_content = file_content[:i] + file_content[i+1:]
            else:
                stack.pop()
    
    # Remove unmatched opening characters
    for char, i in reversed(stack):
        logger.debug(f"Removing unmatched opening character at position {i}")
        file_content = file_content[:i] + file_content[i+1:]
    
    # Enhanced bracket/brace fixing
    file_content = re.sub(r'=\s*([1-9, ]+)(?=\s*(?:#|$))', r'= [\1]', file_content)  # Fix lists
    file_content = re.sub(r'=\s*([1-9, ]+)(?=\s*(?:#|$))', r'= {\1}', file_content)  # Fix sets
    
    # Enhanced nested parentheses handling
    file_content = re.sub(r'\(([^()]+)$', r'(\1)', file_content)  # Fix unclosed parentheses
    file_content = re.sub(r'\[([^\[\]]+)$', r'[\1]', file_content)  # Fix unclosed brackets
    file_content = re.sub(r'\{([^{}]+)$', r'{\1}', file_content)  # Fix unclosed braces
    
    return file_content

def is_matching_pair(opening, closing):
    """Check if parentheses/brackets/braces match"""
    return (opening == '(' and closing == ')') or \
           (opening == '[' and closing == ']') or \
           (opening == '{' and closing == '}')

def fix_finally_blocks(file_content):
    """Fix empty finally blocks in file content"""
    logger.info("Fixing finally blocks")
    lines = file_content.splitlines()
    fixed_lines = []
    in_finally = False
    added_pass = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if 'finally:' in line:
            logger.debug(f"Found finally block at line {i+1}")
            in_finally = True
            added_pass = False
            fixed_lines.append(line)
        elif in_finally and stripped == "":
            continue
        elif in_finally and not added_pass:
            # Add pass statement only if the finally block is empty
            if not any(stripped.startswith(keyword) for keyword in ["pass", "return", "break", "continue"]):
                # Get proper indentation level
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(" " * indent + "pass  # Added by fix script")
                added_pass = True
            fixed_lines.append(line)
        else:
            in_finally = False
            fixed_lines.append(line)

    return "\n".join(fixed_lines)

def fix_file(file_path):
    """Apply all fixes to a file.

    This function reads the file, applies indentation, parentheses,
    and finally block fixes, and writes the corrected content back.
    It handles UnicodeDecodeError by falling back to latin-1 encoding.
    """
    logger.info(f"Processing file: {file_path}")
    try:
      # This part of the code is a function named `fix_file` that processes a file by applying various
      # fixes to its content. Here's a breakdown of what it does:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        content = fix_indentation(content)
        content = fix_parentheses(content)
        content = fix_finally_blocks(content)
        
        if content != original_content:
            logger.info(f"Changes made to {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            logger.info(f"No changes made to {file_path}")
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    project_dir = Path(".")
    files_to_fix = [Path("test_errors.py")]  # Only process test_errors.py for debugging
    
    # Create backup before making changes
    backup_path = create_backup(files_to_fix, "fix_all_errors")
    logger.info(f"Backup created at {backup_path}")
    
    # Apply fixes
    for file_path in files_to_fix:
        fix_file(file_path)

if __name__ == "__main__":
    main()