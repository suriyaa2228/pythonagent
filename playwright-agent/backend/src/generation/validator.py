"""
Deterministic Script Quality Gate and Framework Validator
==========================================================
Enforces Section 17 & 46 of Architecture Specification:
1. Python AST syntax validation
2. Framework symbol compatibility (Page Objects, methods, fixtures)
3. Prohibited operations / credential security
4. Acceptance criteria coverage verification
"""

import ast
import re
from typing import Any, Dict, List, Optional, Set


class ValidationResult:
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None, warnings: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": "PASS" if self.is_valid else "FAIL",
            "isValid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class FrameworkValidator:
    PROHIBITED_IMPORTS = {"os", "sys", "subprocess", "shutil", "socket", "requests", "urllib", "selenium"}
    PROHIBITED_CALLS = {"eval", "exec", "__import__", "compile", "open"}

    def __init__(self, symbol_registry: Optional[Dict[str, Any]] = None):
        self.symbol_registry = symbol_registry or {}
        self.known_page_objects = self.symbol_registry.get("page_objects", {})
        self.known_fixtures = self.symbol_registry.get("fixtures", {})
        self.known_utilities = self.symbol_registry.get("utilities", {})

    def validate_script(self, python_code: str, acceptance_criteria: Optional[List[str]] = None) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not python_code or not python_code.strip():
            return ValidationResult(is_valid=False, errors=["Empty script provided."])

        # 1. AST Syntax Check
        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            return ValidationResult(is_valid=False, errors=[f"Python Syntax Error at line {e.lineno}: {e.msg}"])
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[f"AST Compilation Error: {str(e)}"])

        # 2. Security & Prohibited Operations Check
        for node in ast.walk(tree):
            # Check prohibited imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    if root_pkg in self.PROHIBITED_IMPORTS:
                        errors.append(f"Security Violation: Prohibited import '{alias.name}'.")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    if root_pkg in self.PROHIBITED_IMPORTS:
                        errors.append(f"Security Violation: Prohibited import from '{node.module}'.")

            # Check prohibited calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.PROHIBITED_CALLS:
                    errors.append(f"Security Violation: Prohibited built-in call '{node.func.id}()'.")

        # 3. Hardcoded Credentials Check
        if re.search(r'''password\s*=\s*["'][^"'\n]+["']''', python_code, re.IGNORECASE):
            if 'env_config["password"]' not in python_code and "env_config['password']" not in python_code:
                warnings.append("Potential hardcoded password detected. Always use env_config['password'].")

        # 4. Reporter Integration Check
        has_reporter_import = "Reporter" in python_code and "python_playwright.utils.reporter" in python_code
        has_start_test_case = "Reporter.start_test_case" in python_code
        if not has_reporter_import or not has_start_test_case:
            errors.append("Framework Compliance Error: Test must import and call Reporter.start_test_case(...).")

        # 5. Playwright / Pytest Conventions Check
        has_pytest = "import pytest" in python_code or "from pytest" in python_code
        if not has_pytest:
            errors.append("Framework Compliance Error: Missing 'import pytest'.")

        # 6. Page Object Method Symbol Check
        if self.known_page_objects:
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check method calls on known Page Objects if identifiable
                    if isinstance(node.func, ast.Attribute):
                        method_name = node.func.attr
                        # If calling on an explicit class instance like HomePage(page).method()
                        if isinstance(node.func.value, ast.Call) and isinstance(node.func.value.func, ast.Name):
                            cls_name = node.func.value.func.id
                            if cls_name in self.known_page_objects:
                                callable_methods = self.known_page_objects[cls_name].get("all_callable_methods", [])
                                if callable_methods and method_name not in callable_methods:
                                    errors.append(
                                        f"Symbol Error: Method '{method_name}()' does not exist on '{cls_name}'."
                                    )

        # 7. Acceptance Criteria Coverage Check (if provided)
        if acceptance_criteria:
            for i, ac in enumerate(acceptance_criteria, 1):
                # Basic token coverage heuristic: at least some keywords from the AC appear in the script
                ac_keywords = [w.lower() for w in re.findall(r'\b\w{4,}\b', ac) if w.lower() not in {"user", "should", "able", "with", "that", "from"}]
                if ac_keywords:
                    found_kw = any(kw in python_code.lower() for kw in ac_keywords)
                    if not found_kw:
                        warnings.append(f"Acceptance Criterion {i} ('{ac[:40]}...') may not be covered in test steps.")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
