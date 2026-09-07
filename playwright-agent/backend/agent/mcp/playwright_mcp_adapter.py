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
        headless: bool = False
    ) -> Dict[str, Any]:
        """
        Executes a batch of regression test scripts using Playwright MCP tool tracing
        and live session telemetry.
        """
        import sys
        import subprocess

        start_time = time.time()
        tool_logs = []
        passed_count = 0
        failed_count = 0
        healed_cases = []

        try:
            for test_info in test_infos:
                t_id = test_info.get("testId", "UNKNOWN")
                raw_path = test_info.get("path", "")

                full_path = raw_path if os.path.isabs(raw_path) else os.path.abspath(os.path.join(self.base_dir, raw_path))

                tool_logs.append({
                    "step": len(tool_logs) + 1,
                    "tool": "playwright_mcp_test_start",
                    "testId": t_id,
                    "path": full_path,
                    "status": "EXECUTING"
                })

                # Check if path exists
                if not os.path.exists(full_path):
                    failed_count += 1
                    tool_logs.append({
                        "step": len(tool_logs) + 1,
                        "tool": "playwright_mcp_test_end",
                        "testId": t_id,
                        "status": "FAILED",
                        "error": f"Test script file not found: {full_path}"
                    })
                    continue

                playwright_cwd = os.path.join(self.base_dir, "python_playwright")
                rel_test_path = os.path.relpath(full_path, playwright_cwd)

                env = os.environ.copy()
                env["PYTHONPATH"] = self.base_dir
                env["TEST_ENVIRONMENT"] = environment

                # Run script with pytest via active python executable under python_playwright CWD
                mode_flag = "--headless" if headless else "--headed"
                cmd = [sys.executable, "-m", "pytest", rel_test_path, f"--env={environment}", mode_flag]
                try:
                    proc = subprocess.run(
                        cmd,
                        cwd=playwright_cwd,
                        capture_output=True,
                        text=True,
                        timeout=300,
                        env=env
                    )

                    if proc.returncode == 0:
                        passed_count += 1
                        tool_logs.append({
                            "step": len(tool_logs) + 1,
                            "tool": "playwright_mcp_test_end",
                            "testId": t_id,
                            "status": "PASSED",
                            "stdout": proc.stdout[:500]
                        })
                    else:
                        failed_count += 1
                        tool_logs.append({
                            "step": len(tool_logs) + 1,
                            "tool": "playwright_mcp_test_end",
                            "testId": t_id,
                            "status": "FAILED",
                            "stderr": proc.stderr[:500] or proc.stdout[:500]
                        })
                except subprocess.TimeoutExpired:
                    failed_count += 1
                    tool_logs.append({
                        "step": len(tool_logs) + 1,
                        "tool": "playwright_mcp_test_end",
                        "testId": t_id,
                        "status": "FAILED",
                        "error": "Execution timed out (exceeded 300s limit)."
                    })
        finally:
            self.stop_session()

        duration = round(time.time() - start_time, 2)
        return {
            "executionEngine": "PLAYWRIGHT_MCP_AGENT",
            "environment": environment,
            "durationSeconds": duration,
            "totalCases": len(test_infos),
            "passed": passed_count,
            "failed": failed_count,
            "healedCases": healed_cases,
            "mcpToolLog": tool_logs
        }

