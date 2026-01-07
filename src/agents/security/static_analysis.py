import ast
import logging
from typing import List, Tuple

logger = logging.getLogger("agent.static_analysis")

class StaticCodeAnalyzer:
    """
    Epic 11.2: Static Code Analysis (AST).
    Parses generated Python code to detect dangerous imports or function calls.
    Acts as a pre-flight check before any execution (Sandboxed or otherwise).
    """
    
    def __init__(self):
        # Denylist of dangerous modules
        self.banned_imports = {
            "os", "sys", "subprocess", "shutil", "pickle", "socket", 
            "multiprocessing", "threading", "importlib", "builtins"
        }
        
        # Denylist of dangerous built-in functions
        self.banned_calls = {
            "eval", "exec", "compile", "open", "input"
        }

    def analyze(self, code: str) -> Tuple[bool, List[str]]:
        """
        Parses code and returns (IsSafe, ListOfViolations).
        """
        violations = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, [f"Syntax Error: {e.msg}"]
            
        for node in ast.walk(tree):
            # 1. Check Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in self.banned_imports:
                        violations.append(f"Forbidden Import: {alias.name}")
                        
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in self.banned_imports:
                    violations.append(f"Forbidden ImportFrom: {node.module}")
            
            # 2. Check Function Calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.banned_calls:
                        violations.append(f"Forbidden Function Call: {node.func.id}()")
                        
            # 3. Check for 'import' in strings (heuristic for __import__)
            # This is hard to do perfectly with AST, but we catch direct __import__ calls
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "__import__":
                violations.append("Forbidden Function Call: __import__")

        if violations:
            for v in violations:
                logger.warning(f"STATIC ANALYSIS BLOCK: {v}")
            return False, violations
            
        return True, []

# Singleton
static_analyzer = StaticCodeAnalyzer()
