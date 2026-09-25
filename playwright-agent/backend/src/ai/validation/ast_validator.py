"""
AST Validator
=============
Validates Python syntax, AST tree structure, and catches forbidden or dangerous constructs.
"""

import ast
from typing import List, Tuple


class ASTValidator:
    def validate(self, python_code: str) -> Tuple[bool, List[str]]:
        errors = []
        if not python_code or not python_code.strip():
            return False, ["Script content is empty."]

        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            return False, [f"Python SyntaxError on line {e.lineno}: {e.msg}"]
        except Exception as e:
            return False, [f"Python Parse Exception: {str(e)}"]

        # Check for prohibited AST constructs (e.g., eval, exec, os.system, subprocess)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
                    errors.append(f"Forbidden function call '{node.func.id}' detected on line {node.lineno}.")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"system", "popen", "spawn"} and isinstance(node.func.value, ast.Name) and node.func.value.id in {"os", "subprocess"}:
                        errors.append(f"Forbidden OS command '{node.func.attr}' detected on line {node.lineno}.")

        return (len(errors) == 0, errors)
