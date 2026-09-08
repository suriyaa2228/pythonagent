"""
Playwright Model Control Plane (MCP) Adapter
=============================================
Bridges official Playwright MCP JSON-RPC tool-calling interfaces with the framework's
Python Playwright browser engine and multi-agent regression runner.
"""

import os
import json
import time
from typing import Any, Dict, List, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext


class PlaywrightMcpAdapter:
    """
    Exposes Model Control Plane (MCP) browser tool calls for interactive agent sessions
    and agentic regression suite execution.
    """
    def __init__(self, headless: bool = True, base_dir: Optional[str] = None):
        self.headless = headless
        if not base_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = base_dir
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def start_session(self, viewport: Dict[str, int] = None):
        if not self._playwright:
            try:
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(
                    headless=self.headless,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                self._context = self._browser.new_context(
                    viewport=viewport or {"width": 1440, "height": 900},
                    ignore_https_errors=True
                )
                self._page = self._context.new_page()
            except Exception as e:
                print(f"[WARN] Playwright session start note: {e}")

    def stop_session(self):
        if self._context:
            try:
                self._context.close()
            except Exception:
                pass
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception:
                pass
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None

    # --- MCP Tool Handlers ---

    def navigate(self, url: str) -> Dict[str, Any]:
        """MCP Tool: playwright_navigate"""
        self.start_session()
        if not self._page:
            return {"tool": "playwright_navigate", "status": "ERROR", "error": "No active browser session"}
        try:
            response = self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
            status_code = response.status if response else 200
            return {
                "tool": "playwright_navigate",
                "status": "SUCCESS",
                "url": self._page.url,
                "statusCode": status_code,
                "title": self._page.title()
            }
        except Exception as e:
            return {"tool": "playwright_navigate", "status": "ERROR", "error": str(e)}

    def click(self, selector: str) -> Dict[str, Any]:
        """MCP Tool: playwright_click"""
        if not self._page:
            return {"tool": "playwright_click", "status": "ERROR", "error": "No active browser session"}
        try:
            self._page.click(selector, timeout=15000)
            return {"tool": "playwright_click", "status": "SUCCESS", "selector": selector}
        except Exception as e:
            return {"tool": "playwright_click", "status": "ERROR", "selector": selector, "error": str(e)}

    def fill(self, selector: str, text: str) -> Dict[str, Any]:
        """MCP Tool: playwright_fill"""
        if not self._page:
            return {"tool": "playwright_fill", "status": "ERROR", "error": "No active browser session"}
        try:
            self._page.fill(selector, text, timeout=15000)
            return {"tool": "playwright_fill", "status": "SUCCESS", "selector": selector}
        except Exception as e:
            return {"tool": "playwright_fill", "status": "ERROR", "selector": selector, "error": str(e)}

    def screenshot(self, output_path: str) -> Dict[str, Any]:
        """MCP Tool: playwright_screenshot"""
        if not self._page:
            return {"tool": "playwright_screenshot", "status": "ERROR", "error": "No active browser session"}
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            self._page.screenshot(path=output_path, full_page=True)
            return {"tool": "playwright_screenshot", "status": "SUCCESS", "path": output_path}
        except Exception as e:
            return {"tool": "playwright_screenshot", "status": "ERROR", "error": str(e)}

    def get_content(self) -> Dict[str, Any]:
        """MCP Tool: playwright_get_content"""
        if not self._page:
            return {"tool": "playwright_get_content", "status": "ERROR", "error": "No active browser session"}
        try:
            content = self._page.content()
            return {"tool": "playwright_get_content", "status": "SUCCESS", "contentLength": len(content), "contentExcerpt": content[:2000]}
        except Exception as e:
            return {"tool": "playwright_get_content", "status": "ERROR", "error": str(e)}

    def run_agentic_regression(
        self,
        test_infos: List[Dict[str, Any]],
        environment: str = "stage",
        headless: bool = False,
        execution_id: Optional[str] = None,
        executions_store: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Executes a batch of regression test scripts using Playwright MCP tool tracing
        and live session telemetry with real-time execution progress updates.
        """
        import sys
        import subprocess

        start_time = time.time()
        tool_logs = []
        passed_count = 0
        failed_count = 0
        healed_cases = []
        total_tests = len(test_infos)
        completed_tests = 0
        current_test_index = 1
        test_names = [t.get("testId") or t.get("name") or "Test" for t in test_infos]
        current_test = test_names[0] if test_names else ""

        if executions_store is not None and execution_id and execution_id in executions_store:
            executions_store[execution_id].update({
                "total_tests": total_tests,
                "completed_tests": 0,
                "current_test": current_test,
                "current_test_index": 1,
                "progress_percent": 0,
                "status": "EXECUTING"
            })

        try:
            playwright_cwd = os.path.join(self.base_dir, "python_playwright")
            env = os.environ.copy()
            env["PYTHONPATH"] = self.base_dir
            env["TEST_ENVIRONMENT"] = environment
            mode_flags = ["--headless"] if headless else []

            valid_paths = []
            test_id_map = {}
            for test_info in test_infos:
                t_id = test_info.get("testId", "UNKNOWN")
                raw_path = test_info.get("path", "")
                if raw_path.startswith("backend/") or raw_path.startswith("backend\\"):
                    raw_path = raw_path[8:]
                full_path = raw_path if os.path.isabs(raw_path) else os.path.abspath(os.path.join(self.base_dir, raw_path))

                if os.path.exists(full_path):
                    rel_test_path = os.path.relpath(full_path, playwright_cwd)
                    valid_paths.append(rel_test_path)
                    test_id_map[rel_test_path] = t_id
                    tool_logs.append({
                        "step": len(tool_logs) + 1,
                        "tool": "playwright_mcp_test_start",
                        "testId": t_id,
                        "path": full_path,
                        "status": "EXECUTING"
                    })
                else:
                    failed_count += 1
                    tool_logs.append({
                        "step": len(tool_logs) + 1,
                        "tool": "playwright_mcp_test_missing",
                        "testId": t_id,
                        "status": "FAILED",
                        "error": f"Test script file not found: {full_path}"
                    })

            if valid_paths:
                xml_report_path = os.path.join(playwright_cwd, f"mcp_results_{int(time.time())}.xml")
                cmd = [sys.executable, "-m", "pytest", "-v", f"--junitxml={xml_report_path}"] + valid_paths + [f"--env={environment}"] + mode_flags
                stdout_lines = []
                stderr_lines = []
                try:
                    proc = subprocess.Popen(
                        cmd,
                        cwd=playwright_cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        env=env
                    )

                    for line in iter(proc.stdout.readline, ''):
                        if not line:
                            break
                        stdout_lines.append(line)
                        clean_line = line.strip()

                        # Real-time progress tracking
                        for idx, t_name in enumerate(test_names):
                            if t_name in clean_line or (idx < len(valid_paths) and valid_paths[idx] in clean_line):
                                current_test = t_name
                                current_test_index = idx + 1
                                break

                        if "PASSED" in clean_line or "FAILED" in clean_line or "SKIPPED" in clean_line:
                            completed_tests = min(completed_tests + 1, total_tests)

                        pct = int((completed_tests / total_tests) * 100) if total_tests > 0 else 0

                        if executions_store is not None and execution_id and execution_id in executions_store:
                            executions_store[execution_id].update({
                                "completed_tests": completed_tests,
                                "current_test": current_test,
                                "current_test_index": current_test_index,
                                "progress_percent": pct,
                                "stdout": "".join(stdout_lines)
                            })

                    stderr_out = proc.stderr.read()
                    if stderr_out:
                        stderr_lines.append(stderr_out)

                    proc.wait()
                    stdout_text = "".join(stdout_lines)
                    stderr_text = "".join(stderr_lines)
                    lines = stdout_text.splitlines()

                    # Parse JUnit XML if generated
                    parsed_results = {}
                    if os.path.exists(xml_report_path):
                        try:
                            import xml.etree.ElementTree as ET
                            tree = ET.parse(xml_report_path)
                            root = tree.getroot()
                            for tc in root.findall(".//testcase"):
                                tc_file = tc.get("file", "")
                                tc_name = tc.get("name", "")
                                failure_node = tc.find("failure")
                                error_node = tc.find("error")
                                skipped_node = tc.find("skipped")
                                
                                err_msg = None
                                if failure_node is not None or error_node is not None:
                                    node = failure_node if failure_node is not None else error_node
                                    status = "FAILED"
                                    err_msg = node.get("message") or (node.text or "Test execution failed").strip()
                                elif skipped_node is not None:
                                    status = "SKIPPED"
                                else:
                                    status = "PASSED"
                                    
                                file_key = os.path.basename(tc_file) if tc_file else ""
                                parsed_results[file_key] = {"status": status, "error": err_msg}
                        except Exception as parse_err:
                            print(f"[WARN] JUnit XML parse failed: {parse_err}")
                        finally:
                            try:
                                os.remove(xml_report_path)
                            except Exception:
                                pass

                    for test_info in test_infos:
                        t_id = test_info.get("testId", "UNKNOWN")
                        raw_path = test_info.get("path", "")
                        if raw_path.startswith("backend/") or raw_path.startswith("backend\\"):
                            raw_path = raw_path[8:]
                        full_path = raw_path if os.path.isabs(raw_path) else os.path.abspath(os.path.join(self.base_dir, raw_path))

                        if not os.path.exists(full_path):
                            continue

                        file_name = os.path.basename(full_path)
                        stem = os.path.splitext(file_name)[0]

                        outcome = None
                        error_msg = None

                        if file_name in parsed_results:
                            outcome = parsed_results[file_name]["status"]
                            error_msg = parsed_results[file_name]["error"]
                        else:
                            # Check for pass / fail in pytest output for this specific test file
                            matching_lines = [l for l in lines if stem in l or file_name in l]
                            for l in matching_lines:
                                if "PASSED" in l:
                                    outcome = "PASSED"
                                    break
                                elif "FAILED" in l or "ERROR" in l:
                                    outcome = "FAILED"
                                    break
                                elif "SKIPPED" in l:
                                    outcome = "SKIPPED"
                                    break

                        if not outcome:
                            outcome = "PASSED" if proc.returncode == 0 else "FAILED"

                        if outcome in ["PASSED", "SKIPPED"]:
                            passed_count += 1
                        else:
                            failed_count += 1

                        tool_entry = {
                            "step": len(tool_logs) + 1,
                            "tool": "playwright_mcp_test_end",
                            "testId": t_id,
                            "status": outcome,
                            "script": file_name
                        }
                        if error_msg:
                            tool_entry["error"] = error_msg[:500]
                        tool_logs.append(tool_entry)

                    if stderr_text.strip():
                        tool_logs.append({
                            "step": len(tool_logs) + 1,
                            "tool": "playwright_mcp_stderr_log",
                            "status": "INFO",
                            "stderr": stderr_text[:1000]
                        })

                except Exception as exec_err:
                    failed_count += len(valid_paths)
                    tool_logs.append({
                        "step": len(tool_logs) + 1,
                        "tool": "playwright_mcp_suite_end",
                        "status": "FAILED",
                        "error": str(exec_err)
                    })

        finally:
            self.stop_session()

        duration = round(time.time() - start_time, 2)
        res_summary = {
            "executionEngine": "PLAYWRIGHT_MCP_AGENT",
            "environment": environment,
            "durationSeconds": duration,
            "totalCases": len(test_infos),
            "passed": passed_count,
            "failed": failed_count,
            "healedCases": healed_cases,
            "mcpToolLog": tool_logs
        }

        if executions_store is not None and execution_id and execution_id in executions_store:
            executions_store[execution_id].update({
                "completed_tests": total_tests,
                "progress_percent": 100,
                "status": "PASSED" if failed_count == 0 else "FAILED",
                "duration": duration,
                "mcpResult": res_summary
            })

        return res_summary


