"""
CLI to run the Framework Scanner and generate the Symbol Registry.
"""

import json
import os
import sys

# Ensure src is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, os.path.dirname(current_dir))

from discovery.framework_scanner import FrameworkScanner


def main():
    playwright_dir = os.path.join(agent_dir, "python_playwright")
    output_dir = os.path.join(agent_dir, "data")
    output_file = os.path.join(output_dir, "framework_symbol_registry.json")

    os.makedirs(output_dir, exist_ok=True)

    print(f"Scanning framework at: {playwright_dir}")
    scanner = FrameworkScanner(playwright_dir)
    registry = scanner.scan_all()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    print(f"\n[SUCCESS] Framework Symbol Registry generated at: {output_file}")
    print(f"- Page Objects discovered: {len(registry.get('page_objects', {}))}")
    print(f"- Fixtures discovered: {len(registry.get('fixtures', {}))}")
    print(f"- Utilities discovered: {len(registry.get('utilities', {}))}")
    print(f"- Environments configured: {list(registry.get('config', {}).get('environments', {}).keys())}")


if __name__ == "__main__":
    main()
