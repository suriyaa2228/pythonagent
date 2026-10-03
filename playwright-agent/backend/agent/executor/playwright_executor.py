import subprocess
import os
import sys
import time

class PlaywrightExecutor:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def execute(self, test_info: dict, environment: str, execution_id: str = None, executions_store: dict = None) -> dict:
        return self.execute_batch([test_info], environment, execution_id, executions_store)

    def execute_batch(self, test_infos: list[dict], environment: str, execution_id: str = None, executions_store: dict = None, active_processes: dict = None, current_idx: int = 1, total_count: int = 1) -> dict:
        start_time = time.time()
        
        playwright_cwd = os.path.join(self.base_dir, "python_playwright")
        env = os.environ.copy()
        env["PYTHONPATH"] = self.base_dir
        env["TEST_ENVIRONMENT"] = environment
        
        test_paths = []
        test_names = []
        for test_info in test_infos:
            if not test_info:
                continue
            t_id = test_info.get("testId") or test_info.get("name") or "Test"
            script_path = test_info.get("path", "")
            if script_path:
                full_script_path = os.path.join(self.base_dir, script_path)
                if not os.path.exists(full_script_path):
                    # Fallback check for alternate path separator / underscore variations
                    alt_path = full_script_path.replace("test_tc_", "test_tc") if "test_tc_" in full_script_path else full_script_path.replace("test_tc", "test_tc_")
                    if os.path.exists(alt_path):
                        full_script_path = alt_path

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

        cmd = [sys.executable, "-m", "pytest", "-v", "-s"] + test_paths + [f"--env={environment}", "--headless"]

        current_test = test_names[0] if test_names else ""
        pct_base = int(((current_idx - 1) / total_count) * 100) if total_count > 0 else 0

        if executions_store is not None and execution_id and execution_id in executions_store:
            executions_store[execution_id].update({
                "total_tests": total_count,
                "current_test": current_test,
                "current_test_index": current_idx,
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

            if active_processes is not None and execution_id:
                active_processes[execution_id] = process

            import re
            completed_steps = 0
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break

                # Check if execution was terminated by user
                if executions_store is not None and execution_id and executions_store.get(execution_id, {}).get("status") == "TERMINATED":
                    try:
                        process.kill()
                    except Exception:
                        pass
                    break

                # Handle active pause loop
                while executions_store is not None and execution_id and executions_store.get(execution_id, {}).get("is_paused", False):
                    if executions_store.get(execution_id, {}).get("status") == "TERMINATED":
                        try:
                            process.kill()
                        except Exception:
                            pass
                        break
                    time.sleep(0.3)

                stdout_lines.append(line)
                clean_line = line.strip()

                # Increment step progress on logged step markers
                if any(marker in clean_line for marker in ["[PASS]", "[WARNING]", "[FAIL]", "[INFO]", "::test_"]):
                    completed_steps += 1

                base_pct = ((current_idx - 1) / total_count) * 100.0
                max_pct = (current_idx / total_count) * 100.0
                step_progress_pct = min(95.0, (completed_steps / 22.0) * 100.0)
                dyn_pct = int(base_pct + (step_progress_pct / 100.0) * (max_pct - base_pct))
                dyn_pct = max(5, min(95, dyn_pct))

                if executions_store is not None and execution_id and execution_id in executions_store:
                    existing_stdout = executions_store[execution_id].get("stdout", "")
                    executions_store[execution_id].update({
                        "stdout": existing_stdout + line,
                        "current_test": current_test,
                        "current_test_index": current_idx,
                        "progress_percent": dyn_pct
                    })

            stderr_out = process.stderr.read()
            if stderr_out:
                stderr_lines.append(stderr_out)

            process.wait()
            if active_processes is not None and execution_id in active_processes:
                active_processes.pop(execution_id, None)

            exit_code = process.returncode
            duration = round(time.time() - start_time, 2)
            
            # Check if terminated
            is_terminated = executions_store is not None and execution_id and executions_store.get(execution_id, {}).get("status") == "TERMINATED"
            final_status = "TERMINATED" if is_terminated else ("PASSED" if exit_code == 0 else "FAILED")

            return {
                "exit_code": exit_code,
                "stdout": "".join(stdout_lines),
                "stderr": "".join(stderr_lines),
                "status": final_status,
                "duration": duration
            }
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            if active_processes is not None and execution_id in active_processes:
                active_processes.pop(execution_id, None)
            return {
                "exit_code": -1,
                "stdout": "".join(stdout_lines),
                "stderr": str(e),
                "status": "FAILED",
                "duration": duration
            }

