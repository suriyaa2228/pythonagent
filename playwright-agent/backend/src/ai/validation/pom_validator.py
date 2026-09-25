"""
POM & Symbol Validator
======================
Validates Page Object Model compliance, ensures methods called on Page Objects exist
in the Symbol Registry, and prevents hallucinated locators or methods.
"""

import ast
from typing import List, Tuple, Dict, Any


class POMValidator:
    def __init__(self, symbol_registry: Dict[str, Any] = None):
        self.symbol_registry = symbol_registry or {}
        self.page_objects = self.symbol_registry.get("page_objects", {})

    def validate(self, python_code: str) -> Tuple[bool, List[str]]:
        errors = []
        try:
            tree = ast.parse(python_code)
        except Exception:
            return False, ["AST parsing failed for POM validation."]

        # Map variable instances to Page Object classes
        var_to_class: Dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    class_name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
                    if class_name in self.page_objects:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                var_to_class[target.id] = class_name

        # Verify method calls on mapped variables
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                obj_name = node.func.value.id if isinstance(node.func.value, ast.Name) else None
                method_name = node.func.attr

                if obj_name in var_to_class:
                    cls_name = var_to_class[obj_name]
                    cls_info = self.page_objects.get(cls_name, {})
                    callable_methods = cls_info.get("all_callable_methods", list(cls_info.get("methods", {}).keys()))
                    if method_name not in callable_methods:
                        errors.append(f"Hallucinated method '{method_name}' called on '{cls_name}' (instance '{obj_name}') on line {node.lineno}.")

        return (len(errors) == 0, errors)
