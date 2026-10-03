import os
import json
import re
import yaml
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from models.task import SaveTestCaseRequest, TestCaseModel, TestCaseMetadata


class TestCaseRepository:
    def __init__(self, base_dir: Optional[str] = None):
        if not base_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = base_dir
        self.tests_dir = os.path.join(self.base_dir, "python_playwright", "tests")
        self.data_dir = os.path.join(self.base_dir, "data")
        self.metadata_file = os.path.join(self.data_dir, "test_cases.json")
        self.yaml_registry_file = os.path.join(self.base_dir, "config", "test_registry.yaml")

        os.makedirs(self.tests_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def _sanitize_name(self, name: str) -> str:
        """Sanitizes test case name for safe file naming."""
        clean = re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip())
        clean = re.sub(r'_+', '_', clean)
        return clean.strip('_').lower()

    def _load_metadata_store(self) -> Dict[str, Any]:
        if not os.path.exists(self.metadata_file):
            return {}
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_metadata_store(self, data: Dict[str, Any]):
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _update_yaml_registry(self, test_id: str, name: str, relative_path: str):
        registry_data = {}
        if os.path.exists(self.yaml_registry_file):
            try:
                with open(self.yaml_registry_file, "r", encoding="utf-8") as f:
                    registry_data = yaml.safe_load(f) or {}
            except Exception:
                registry_data = {}

        registry_data[test_id] = {
            "name": name,
            "type": "pytest",
            "path": relative_path.replace("\\", "/"),
            "enabled": True
        }

        with open(self.yaml_registry_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(registry_data, f, sort_keys=False)

    def save_test_case(self, req: SaveTestCaseRequest) -> Dict[str, Any]:
        clean_num = self._sanitize_name(req.testCaseNumber).upper()
        clean_name = self._sanitize_name(req.testCaseName)

        if not clean_num or not clean_name:
            raise ValueError("Test Case Number and Test Case Name are mandatory.")

        clean_num_file = clean_num.lower().replace("_", "")
        file_basename = f"test_{clean_num_file}_{clean_name}.py"
        target_path = os.path.join(self.tests_dir, file_basename)
        relative_path = os.path.join("python_playwright", "tests", file_basename)

        # Write Python script file
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(req.pythonScript)

        now_iso = datetime.now(timezone.utc).isoformat()
        test_id = f"{clean_num}_{clean_name.upper()}"

        tc_model = TestCaseModel(
            id=test_id,
            number=req.testCaseNumber.strip(),
            name=req.testCaseName.strip(),
            status="SAVED",
            scripts={"python": target_path},
            metadata=TestCaseMetadata(
                author="AI_Agent",
                created_at=now_iso,
                updated_at=now_iso,
                environment=req.environment or "stage",
                tags=["AI_Generated", "Saved_Workspace"]
            )
        )

        # Persist JSON metadata
        store = self._load_metadata_store()
        store[test_id] = tc_model.model_dump()
        self._save_metadata_store(store)

        # Update test_registry.yaml so TestRegistry picks it up immediately
        display_name = f"{req.testCaseNumber.strip()} {req.testCaseName.strip()}"
        self._update_yaml_registry(test_id, display_name, relative_path)

        return {
            "testId": test_id,
            "testCaseNumber": req.testCaseNumber,
            "testCaseName": req.testCaseName,
            "filePath": target_path,
            "relativePath": relative_path,
            "status": "SAVED"
        }

    def get_test_case(self, test_id: str) -> Optional[Dict[str, Any]]:
        store = self._load_metadata_store()
        return store.get(test_id)

    def delete_test_case(self, test_id: str) -> bool:
        store = self._load_metadata_store()
        if test_id in store:
            del store[test_id]
            self._save_metadata_store(store)
        if os.path.exists(self.yaml_registry_file):
            try:
                with open(self.yaml_registry_file, "r", encoding="utf-8") as f:
                    registry_data = yaml.safe_load(f) or {}
                if test_id in registry_data:
                    del registry_data[test_id]
                    with open(self.yaml_registry_file, "w", encoding="utf-8") as f:
                        yaml.safe_dump(registry_data, f, sort_keys=False)
            except Exception:
                pass
        return True
