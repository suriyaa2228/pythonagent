import subprocess
import os
import time

class PlaywrightExecutor:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def execute(self, test_info: dict, environment: str) -> dict:
        start_time = time.time()
        
        script_path = test_info.get("path", "")
        test_type = test_info.get("type", "python_script")
        full_script_path = os.path.join(self.base_dir, script_path)
        
        if not os.path.exists(full_script_path):
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": f"Script not found: {full_script_path}",
                "status": "FAILED",
                "duration": time.time() - start_time
            }

        playwright_cwd = os.path.join(self.base_dir, "python_playwright")
        rel_test_path = os.path.relpath(full_script_path, playwright_cwd)

        env = os.environ.copy()
        env["PYTHONPATH"] = self.base_dir
        env["TEST_ENVIRONMENT"] = environment
        
        try:
            if test_type == "pytest":
                cmd = ["pytest", rel_test_path, f"--env={environment}", "--headless"]
            else:
                cmd = ["python", full_script_path]
                
            result = subprocess.run(
                cmd,
                cwd=playwright_cwd,
                capture_output=True,
                text=True,
                env=env
            )
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "status": "FAILED",
                "duration": time.time() - start_time
            }

    def execute_batch(self, test_infos: list[dict], environment: str) -> dict:
        start_time = time.time()
        
        playwright_cwd = os.path.join(self.base_dir, "python_playwright")
        env = os.environ.copy()
        env["PYTHONPATH"] = self.base_dir
        env["TEST_ENVIRONMENT"] = environment
        
        cmd = ["pytest"]
        for test_info in test_infos:
            script_path = test_info.get("path", "")
            if script_path:
                full_script_path = os.path.join(self.base_dir, script_path)
                rel_test_path = os.path.relpath(full_script_path, playwright_cwd)
                cmd.append(rel_test_path)
                
        cmd.extend([f"--env={environment}", "--headless"])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=playwright_cwd,
                capture_output=True,
                text=True,
                env=env
            )
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "status": "FAILED",
                "duration": time.time() - start_time
            }
