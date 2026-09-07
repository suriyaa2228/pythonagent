"""
Controlled Subprocess Execution Engine
======================================
Spawns pytest executions in isolated per-execution workspaces with real-time logging,
strictly preserving the existing Python Playwright framework execution target.
"""

import datetime
import os
import shutil
import subprocess
import uuid
from typing import Any, Dict, Optional


class ExecutionResult:
    def __init__(
        self,
        execution_id: str,
        status: str,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration_seconds: float,
        report_path: Optional[str] = None
    ):
        self.execution_id = execution_id
        self.status = status  # "PASSED", "FAILED", "ERROR"
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_seconds = duration_seconds
        self.report_path = report_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "executionId": self.execution_id,
            "status": self.status,
            "exitCode": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "durationSeconds": round(self.duration_seconds, 2),
            "reportPath": self.report_path
        }


class TestRunner:
    def __init__(self, agent_root: str):
        self.agent_root = os.path.abspath(agent_root)
        self.playwright_dir = os.path.join(self.agent_root, "python_playwright")
        self.executions_dir = os.path.join(self.agent_root, "executions")
        self.reports_dir = os.path.join(self.playwright_dir, "reports")
        os.makedirs(self.executions_dir, exist_ok=True)

    def execute_script(
        self,
        python_script: str,
        test_name: str = "test_generated_tc.py",
        headless: bool = True,
        env_name: str = "stage"
    ) -> ExecutionResult:
        """
        Provisions an isolated execution workspace and runs pytest securely via argument arrays.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        exec_id = f"EXEC-{timestamp}-{uuid.uuid4().hex[:6]}"
        workspace = os.path.join(self.executions_dir, exec_id)
        os.makedirs(workspace, exist_ok=True)

        test_file_path = os.path.join(self.playwright_dir, "tests", test_name)
        
        # Write test file into python_playwright/tests
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(python_script)

        # Copy a backup into the execution workspace
        shutil.copy2(test_file_path, os.path.join(workspace, test_name))

        # Build controlled pytest argument array (NEVER shell string)
        cmd = [
            "pytest",
            f"tests/{test_name}",
            f"--env={env_name}"
        ]
        if headless:
            cmd.append("--headless")

        start_time = datetime.datetime.now()

        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.playwright_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PYTHONPATH": self.agent_root}
            )
            stdout, stderr = process.communicate(timeout=180)
            exit_code = process.returncode
            status = "PASSED" if exit_code == 0 else "FAILED"
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            exit_code = -1
            status = "TIMEOUT"
        except Exception as e:
            stdout = ""
            stderr = str(e)
            exit_code = -1
            status = "ERROR"

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Write execution logs to workspace
        with open(os.path.join(workspace, "stdout.log"), "w", encoding="utf-8") as f:
            f.write(stdout)
        with open(os.path.join(workspace, "stderr.log"), "w", encoding="utf-8") as f:
            f.write(stderr)

        # Find latest Extent Report
        latest_report = self._find_latest_extent_report()

        return ExecutionResult(
            execution_id=exec_id,
            status=status,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            report_path=latest_report
        )

    def _find_latest_extent_report(self) -> Optional[str]:
        """Finds the most recent Extent HTML report."""
        if not os.path.exists(self.reports_dir):
            return None
        reports = [
            os.path.join(self.reports_dir, f)
            for f in os.listdir(self.reports_dir)
            if f.startswith("extent_report_") and f.endswith(".html")
        ]
        if not reports:
            return None
        reports.sort(key=os.path.getmtime, reverse=True)
        return reports[0]
