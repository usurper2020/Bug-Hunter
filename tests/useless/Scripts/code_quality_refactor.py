import os
import ast
import radon.complexity as radon_complexity
import radon.metrics as radon_metrics
import radon.visitors as radon_visitors
import autopep8

class CodeQualityRefactor:
    def __init__(self, directory):
        self.directory = directory

    def analyze_file(self, file_path):
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read(), filename=file_path)
            visitor = radon_visitors.ComplexityVisitor.from_ast(tree)
            return visitor.functions

    def analyze_directory(self):
        results = {}
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    results[file_path] = self.analyze_file(file_path)
        return results

    def print_analysis(self, analysis):
        for file_path, functions in analysis.items():
            print(f"File: {file_path}")
            for function in functions:
                print(f"  Function: {function.name}")
                print(f"    Complexity: {function.complexity}")
                print(f"    Lines: {function.lineno}-{function.endline}")
                print(f"    Parameters: {len(function.args.args)}")
                print()

    def refactor_file(self, file_path):
        with open(file_path, 'r') as file:
            code = file.read()
        formatted_code = autopep8.fix_code(code)
        with open(file_path, 'w') as file:
            file.write(formatted_code)

    def refactor_directory(self):
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.refactor_file(file_path)

if __name__ == "__main__":
    directory = "app"  # Change this to the directory you want to analyze and refactor
    code_quality_refactor = CodeQualityRefactor(directory)
    
    print("Analyzing code quality...")
    analysis = code_quality_refactor.analyze_directory()
    code_quality_refactor.print_analysis(analysis)
    
    print("Refactoring code...")
    code_quality_refactor.refactor_directory()
    print("Refactoring completed.")