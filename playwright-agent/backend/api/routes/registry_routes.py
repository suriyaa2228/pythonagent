"""
Symbol Registry Routes
======================
Provides API endpoints to query authoritative framework Symbol Registry and Test Patterns.
"""

import os
from typing import Dict, Any
from fastapi import APIRouter
from src.ai.discovery.symbol_registry import SymbolRegistry

router = APIRouter()


@router.get("/symbols")
def get_symbols():
    """Returns the indexed Symbol Registry containing classes, methods, fixtures, and utilities."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "python_playwright"))
    registry = SymbolRegistry.from_framework_dir(root_dir)
    return registry.data


@router.get("/patterns")
def get_patterns():
    """Returns the library of standard Test Patterns."""
    patterns_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "patterns"))
    patterns = []
    if os.path.exists(patterns_dir):
        for root, dirs, files in os.walk(patterns_dir):
            for file in files:
                if file.endswith(".json"):
                    patterns.append(os.path.join(root, file))
    return {"pattern_files": patterns, "count": len(patterns)}
