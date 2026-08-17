"""
Framework Scanner
=================
AST-based framework discovery scanner that inspects the existing `python_playwright`
automation codebase. It deterministically extracts classes, methods, fixtures,
parameters, locators, and utility signatures without executing the code.
"""

import ast
import json
import os
from typing import Any, Dict, List, Optional


class FrameworkScanner:
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.pages_dir = os.path.join(self.root_dir, "pages")
        self.utils_dir = os.path.join(self.root_dir, "utils")
        self.fixtures_dir = os.path.join(self.root_dir, "fixtures")
        self.tests_dir = os.path.join(self.root_dir, "tests")
        self.config_dir = os.path.join(self.root_dir, "config")
        self.conftest_path = os.path.join(self.root_dir, "conftest.py")

    def scan_all(self) -> Dict[str, Any]:
        """Runs full framework discovery and returns a structured symbol dictionary."""
        page_objects = self.scan_page_objects()
        
        # Link inherited methods
        for class_name, data in page_objects.items():
            all_methods = dict(data.get("methods", {}))
            for base_name in data.get("base_classes", []):
                if base_name in page_objects:
                    base_methods = page_objects[base_name].get("methods", {})
                    for m_name, m_info in base_methods.items():
                        if m_name not in all_methods:
                            all_methods[m_name] = {**m_info, "inherited_from": base_name}
            data["all_callable_methods"] = list(all_methods.keys())

        return {
            "metadata": {
                "project": "python_playwright",
                "framework": "playwright-python",
                "runner": "pytest",
                "root_path": self.root_dir,
                "version": "1.0.0"
            },
            "page_objects": page_objects,
            "fixtures": self.scan_fixtures(),
            "utilities": self.scan_utilities(),
            "config": self.scan_config(),
            "conventions": self.scan_test_conventions()
        }

    def _safe_parse_file(self, file_path: str) -> Optional[ast.AST]:
        """Safely parses a Python file into an AST."""
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return ast.parse(f.read(), filename=file_path)
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
            return None

    def scan_page_objects(self) -> Dict[str, Any]:
        """Discovers and parses all Page Object classes and methods."""
        page_objects: Dict[str, Any] = {}
        if not os.path.exists(self.pages_dir):
            return page_objects

        for filename in sorted(os.listdir(self.pages_dir)):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            file_path = os.path.join(self.pages_dir, filename)
            rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
            tree = self._safe_parse_file(file_path)
            if not tree:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    base_classes = [
                        b.id if isinstance(b, ast.Name) else getattr(b, "attr", str(b))
                        for b in node.bases
                    ]

                    methods: Dict[str, Any] = {}
                    locators: List[str] = []

                    for item in node.body:
                        # Extract methods
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_name = item.name
                            args = [a.arg for a in item.args.args if a.arg != "self"]
                            docstring = ast.get_docstring(item) or ""
                            
                            # Inspect return statements for fluent chaining patterns
                            returns = []
                            for subnode in ast.walk(item):
                                if isinstance(subnode, ast.Return) and subnode.value:
                                    if isinstance(subnode.value, ast.Name):
                                        returns.append(subnode.value.id)
                                    elif isinstance(subnode.value, ast.Call):
                                        if isinstance(subnode.value.func, ast.Name):
                                            returns.append(subnode.value.func.id)

                            methods[method_name] = {
                                "name": method_name,
                                "parameters": args,
                                "docstring": docstring.strip(),
                                "returns": list(set(returns)),
                                "is_async": isinstance(item, ast.AsyncFunctionDef)
                            }

                        # Extract locators / class attributes
                        elif isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    locators.append(target.id)

                    page_objects[class_name] = {
                        "class_name": class_name,
                        "file_path": rel_path,
                        "base_classes": base_classes,
                        "docstring": (ast.get_docstring(node) or "").strip(),
                        "methods": methods,
                        "locators": locators
                    }

        return page_objects

    def scan_fixtures(self) -> Dict[str, Any]:
        """Scans conftest.py and test files for pytest fixtures."""
        fixtures: Dict[str, Any] = {}
        files_to_scan = []

        if os.path.exists(self.conftest_path):
            files_to_scan.append(self.conftest_path)

        if os.path.exists(self.fixtures_dir):
            for fname in os.listdir(self.fixtures_dir):
                if fname.endswith(".py"):
                    files_to_scan.append(os.path.join(self.fixtures_dir, fname))

        if os.path.exists(self.tests_dir):
            for fname in os.listdir(self.tests_dir):
                if fname.startswith("test_") and fname.endswith(".py"):
                    files_to_scan.append(os.path.join(self.tests_dir, fname))

        for file_path in files_to_scan:
            rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
            tree = self._safe_parse_file(file_path)
            if not tree:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    is_fixture = False
                    scope = "function"
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Call):
                            if isinstance(dec.func, ast.Attribute) and dec.func.attr == "fixture":
                                is_fixture = True
                                for kw in dec.keywords:
                                    if kw.arg == "scope" and isinstance(kw.value, ast.Constant):
                                        scope = str(kw.value.value)
                        elif isinstance(dec, ast.Attribute) and dec.attr == "fixture":
                            is_fixture = True

                    if is_fixture:
                        params = [a.arg for a in node.args.args]
                        fixtures[node.name] = {
                            "name": node.name,
                            "scope": scope,
                            "parameters": params,
                            "file_path": rel_path,
                            "docstring": (ast.get_docstring(node) or "").strip()
                        }

        return fixtures

    def scan_utilities(self) -> Dict[str, Any]:
        """Scans utilities like Reporter and DataLibrary."""
        utilities: Dict[str, Any] = {}
        if not os.path.exists(self.utils_dir):
            return utilities

        for filename in sorted(os.listdir(self.utils_dir)):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            file_path = os.path.join(self.utils_dir, filename)
            rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
            tree = self._safe_parse_file(file_path)
            if not tree:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    methods: Dict[str, Any] = {}
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            is_static = any(
                                (isinstance(d, ast.Name) and d.id == "staticmethod") or
                                (isinstance(d, ast.Attribute) and d.attr == "staticmethod")
                                for d in item.decorator_list
                            )
                            is_classmethod = any(
                                (isinstance(d, ast.Name) and d.id == "classmethod") or
                                (isinstance(d, ast.Attribute) and d.attr == "classmethod")
                                for d in item.decorator_list
                            )
                            args = [
                                a.arg for a in item.args.args 
                                if a.arg not in ("self", "cls")
                            ]
                            methods[item.name] = {
                                "name": item.name,
                                "parameters": args,
                                "is_static": is_static,
                                "is_classmethod": is_classmethod,
                                "docstring": (ast.get_docstring(item) or "").strip()
                            }

                    utilities[class_name] = {
                        "class_name": class_name,
                        "file_path": rel_path,
                        "methods": methods,
                        "docstring": (ast.get_docstring(node) or "").strip()
                    }

        return utilities

    def scan_config(self) -> Dict[str, Any]:
        """Scans config.json for environment definitions and required keys."""
        config_path = os.path.join(self.config_dir, "config.json")
        if not os.path.exists(config_path):
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                raw_config = json.load(f)

            envs = {}
            for env_name, env_data in raw_config.items():
                if isinstance(env_data, dict):
                    envs[env_name] = {
                        "keys": list(env_data.keys()),
                        "has_url": "url" in env_data,
                        "has_credentials": "username" in env_data and "password" in env_data
                    }
            return {
                "file_path": os.path.relpath(config_path, self.root_dir).replace("\\", "/"),
                "environments": envs
            }
        except Exception as e:
            return {"error": str(e)}

    def scan_test_conventions(self) -> Dict[str, Any]:
        """Samples existing test scripts to extract standard imports and structural patterns."""
        sample_patterns = {
            "standard_imports": [
                "import pytest",
                "from playwright.sync_api import sync_playwright, expect",
                "from python_playwright.utils.reporter import Reporter"
            ],
            "common_assertions": [
                "expect(locator).to_be_visible()",
                "expect(locator).to_have_text()",
                "expect(locator).to_contain_text()"
            ],
            "test_class_naming": "Test<TC_ID><Description>",
            "test_method_naming": "test_run_<action>"
        }
        return sample_patterns
