import yaml
import os

class TestRegistry:
    def __init__(self, config_path: str = None):
        if not config_path:
            # Default to the config folder relative to this file's grand-parent
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, "config", "test_registry.yaml")
            
        self.config_path = config_path
        self.tests = self._load_registry()

    def _load_registry(self) -> dict:
        if not os.path.exists(self.config_path):
            print(f"Warning: Test registry config not found at {self.config_path}")
            return {}
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def reload(self):
        self.tests = self._load_registry()

    def get_test(self, test_id: str) -> dict:
        self.reload()
        return self.tests.get(test_id)

    def test_exists(self, test_id: str) -> bool:
        self.reload()
        return test_id in self.tests and self.tests[test_id].get("enabled", False)

    def get_all_tests(self) -> dict:
        self.reload()
        return {k: v for k, v in self.tests.items() if v.get("enabled", False)}

