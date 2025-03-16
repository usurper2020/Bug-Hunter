import os
import ast
import logging

# Configure logging
logging.basicConfig(filename='code_analysis_log.txt', level=logging.DEBUG, format='%(message)s')

def analyze_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError as e:
        return [f"UnicodeDecodeError: {e.reason} at position {e.start} in file {file_path}"]

    errors = []
    try:
        tree = ast.parse(content, filename=file_path)
    except (SyntaxError, IndentationError) as e:
        errors.append(f"{type(e).__name__}: {e.msg} at line {e.lineno}")
        return errors

    for node in ast.walk(tree):
        if isinstance(node, (ast.Try, ast.ExceptHandler, ast.If)) and not node.body:
            errors.append(f"Empty block detected at line {node.lineno}")
        if isinstance(node, ast.Try) and not node.finalbody:
            errors.append(f"Empty finally block detected at line {node.lineno}")

    return errors

def rate_file(errors):
    error_count = len(errors)
    return max(0, 5 - error_count)

def log_file_analysis(file_path, errors):
    logging.info(f"File: {file_path}")
    if errors:
        for error in errors:
            logging.info(f"  {error}")
    else:
        logging.info("  No errors found.")
    rating = rate_file(errors)
    logging.info(f"Rating: {rating}/5")
    logging.info("")

def analyze_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                errors = analyze_file(file_path)
                log_file_analysis(file_path, errors)

if __name__ == "__main__":
    directory_to_analyze = '.'  # Change this to the directory you want to analyze
    analyze_directory(directory_to_analyze)
    print("Analysis complete. Check 'code_analysis_log.txt' for results.")
