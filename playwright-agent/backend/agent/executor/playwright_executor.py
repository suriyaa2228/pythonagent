import subprocess
import os
import sys
import time

class PlaywrightExecutor:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def execute(self, test_info: dict, environment: str, execution_id: str = None, executions_store: dict = None) -> dict:
        return self.execute_batch([test_info], environment, execution_id, executions_store)

    def execute_batch(self, test_infos: list[dict], environment: str, execution_id: str = None, executions_store: dict = None) -> dict:
        start_time = time.time()
        
        playwright_cwd = os.path.join(self.base_dir, "python_playwright")
        env = os.environ.copy()
        env["PYTHONPATH"] = self.base_dir
        env["TEST_ENVIRONMENT"] = environment
        
        test_paths = []
        test_names = []
        for test_info in test_infos:
            t_id = test_info.get("testId") or test_info.get("name") or "Test"
            script_path = test_info.get("path", "")
            if script_path:
                full_script_path = os.path.join(self.base_dir, script_path)
                if os.path.exists(full_script_path):
                    rel_test_path = os.path.relpath(full_script_path, playwright_cwd)
                    test_paths.append(rel_test_path)
                    test_names.append(t_id)

        if not test_paths:
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": "No valid test script paths found.",
                "status": "FAILED",
                "duration": round(time.time() - start_time, 2)
            }

        # Run all test paths in a single pytest invocation so a single consolidated Extent Report is generated
        cmd = [sys.executable, "-m", "pytest", "-v", "-s"] + test_paths + [f"--env={environment}", "--headless"]

        total_tests = len(test_names)
        completed_tests = 0
        current_test = test_names[0] if test_names else ""
        current_test_index = 1

        if executions_store is not None and execution_id and execution_id in executions_store:
            executions_store[execution_id].update({
                "total_tests": total_tests,
                "completed_tests": 0,
                "current_test": current_test,
                "current_test_index": 1,
                "progress_percent": 0,
                "status": "EXECUTING"
            })

        stdout_lines = []
        stderr_lines = []

        try:
            process = subprocess.Popen(
                cmd,
                cwd=playwright_cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env
            )

            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                stdout_lines.append(line)
                clean_line = line.strip()

                # Live progress tracking
                for idx, t_name in enumerate(test_names):
                    if t_name in clean_line or (idx < len(test_paths) and test_paths[idx] in clean_line):
                        current_test = t_name
                        current_test_index = idx + 1
                        completed_tests = max(completed_tests, idx)
                        break

                if "PASSED" in clean_line or "FAILED" in clean_line or "SKIPPED" in clean_line:
                    completed_tests = min(completed_tests + 1, total_tests)

                progress_pct = int((completed_tests / total_tests) * 100) if total_tests > 0 else 0

                if executions_store is not None and execution_id and execution_id in executions_store:
                    executions_store[execution_id].update({
                        "completed_tests": completed_tests,
                        "current_test": current_test,
                        "current_test_index": current_test_index,
                        "progress_percent": progress_pct,
                        "stdout": "".join(stdout_lines)
                    })

            stderr_out = process.stderr.read()
            if stderr_out:
                stderr_lines.append(stderr_out)

            process.wait()
            exit_code = process.returncode
            duration = round(time.time() - start_time, 2)
            final_status = "PASSED" if exit_code == 0 else "FAILED"

            if executions_store is not None and execution_id and execution_id in executions_store:
                executions_store[execution_id].update({
                    "completed_tests": total_tests,
                    "progress_percent": 100,
                    "status": final_status,
                    "duration": duration,
                    "stdout": "".join(stdout_lines),
                    "stderr": "".join(stderr_lines)
                })

            return {
                "exit_code": exit_code,
                "stdout": "".join(stdout_lines),
                "stderr": "".join(stderr_lines),
                "status": final_status,
                "duration": duration
            }
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            if executions_store is not None and execution_id and execution_id in executions_store:
                executions_store[execution_id].update({
                    "status": "FAILED",
                    "duration": duration,
                    "stderr": str(e)
                })
            return {
                "exit_code": -1,
                "stdout": "".join(stdout_lines),
                "stderr": str(e),
                "status": "FAILED",
                "duration": duration
            }

