"""
Authoritative Framework Symbol Registry
========================================
Implements the Symbol Registry specified in Section 11 of the Target Architecture.
Provides fast, deterministic verification of classes, methods, locators, fixtures, and utilities.
"""

import json
import os
from typing import Any, Dict, List, Optional, Set
from src.discovery.framework_scanner import FrameworkScanner


class SymbolRegistry:
    def __init__(self, registry_data: Optional[Dict[str, Any]] = None):
        self.data = registry_data or {}
        self.classes: Set[str] = set()
        self.methods: Dict[str, Set[str]] = {}
        self.fixtures: Set[str] = set()
        self.utilities: Dict[str, Set[str]] = {}
        self.locators: Dict[str, List[str]] = {}
        self._index_registry()

    @classmethod
    def from_framework_dir(cls, framework_dir: str) -> "SymbolRegistry":
        scanner = FrameworkScanner(framework_dir)
        raw_data = scanner.scan_all()
        return cls(raw_data)

    @classmethod
    def load_from_json(cls, json_path: str) -> "SymbolRegistry":
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(data)
        return cls({})

    def save_to_json(self, json_path: str) -> None:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def _index_registry(self) -> None:
        pobs = self.data.get("page_objects", {})
        for cls_name, info in pobs.items():
            self.classes.add(cls_name)
            self.methods[cls_name] = set(info.get("all_callable_methods", []))
            self.locators[cls_name] = info.get("locators", [])

        fixtures = self.data.get("fixtures", {})
        for fix_name in fixtures:
            self.fixtures.add(fix_name)

        utils = self.data.get("utilities", {})
        for util_name, info in utils.items():
            self.utilities[util_name] = set(info.get("methods", {}).keys())

    def has_class(self, class_name: str) -> bool:
        return class_name in self.classes or class_name in self.utilities

    def has_method(self, class_name: str, method_name: str) -> bool:
        if class_name in self.methods:
            return method_name in self.methods[class_name]
        if class_name in self.utilities:
            return method_name in self.utilities[class_name]
        return False

    def has_fixture(self, fixture_name: str) -> bool:
        return fixture_name in self.fixtures

    def get_symbol_details(self, class_name: str, method_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        pobs = self.data.get("page_objects", {})
        if class_name in pobs:
            cls_info = pobs[class_name]
            if method_name:
                return cls_info.get("methods", {}).get(method_name)
            return cls_info
        return None
