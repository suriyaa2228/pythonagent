"""
Extent Report Parser and Dashboard Adapter
==========================================
Parses existing Extent HTML report files to extract structured JSON statistics,
test case statuses, execution times, and screenshots per Section 26 & 27.
"""

import os
import re
from typing import Any, Dict, List, Optional


class ExtentReportParser:
    def __init__(self, reports_dir: str):
        self.reports_dir = os.path.abspath(reports_dir)

    def list_reports(self) -> List[Dict[str, Any]]:
        """Lists all Extent Reports with file metadata."""
        if not os.path.exists(self.reports_dir):
            return []

        reports = []
        for filename in sorted(os.listdir(self.reports_dir), reverse=True):
            if filename.startswith("extent_report_") and filename.endswith(".html"):
                full_path = os.path.join(self.reports_dir, filename)
                stat = os.stat(full_path)
                reports.append({
                    "fileName": filename,
                    "filePath": full_path,
                    "sizeBytes": stat.st_size,
                    "modifiedTimestamp": stat.st_mtime
                })
        return reports

    def parse_report_file(self, file_path: str) -> Dict[str, Any]:
        """Parses an Extent Report HTML file into a structured summary."""
        if not os.path.exists(file_path):
            return {"error": "Report file not found."}

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        # Extract test cases from sidebar menu items
        menu_items = re.findall(
            r'<div[^>]*class="[^"]*test-menu-item[^"]*"[^>]*>\s*<span[^>]*class="[^"]*status-badge\s+(status-[a-z]+)[^"]*"[^>]*>([^<]+)</span>\s*<span[^>]*class="test-menu-name"[^>]*>([^<]+)</span>',
            html, re.IGNORECASE
        )

        if menu_items:
            flat_test_names = [m[2].strip() for m in menu_items]
            total_cases = len(menu_items)
            passed_cases = sum(1 for m in menu_items if m[1].upper() in ["PASS", "WARNING"])
            failed_cases = sum(1 for m in menu_items if m[1].upper() == "FAIL")
            warn_cases = sum(1 for m in menu_items if m[1].upper() == "WARNING")
            pass_percentage = round((passed_cases / total_cases) * 100, 1) if total_cases > 0 else 100.0
            overall_status = "PASSED" if failed_cases == 0 else "FAILED"

            return {
                "fileName": os.path.basename(file_path),
                "totalTestCases": total_cases,
                "passed": passed_cases,
                "failed": failed_cases,
                "skipped": warn_cases,
                "passPercentage": pass_percentage,
                "testCaseNames": flat_test_names,
                "overallStatus": overall_status
            }

        # Fallback for alternative HTML structures
        test_names = re.findall(r'<p class="name">([^<]+)</p>|<h5 class="test-status[^"]*">([^<]+)</h5>|<span class="test-menu-name">([^<]+)</span>', html)
        flat_test_names = [t[0] or t[1] or t[2] for t in test_names if t[0] or t[1] or t[2]]

        pass_steps = len(re.findall(r'<td>\s*<span[^>]*class="[^"]*(?:status-pass|pass-bg)[^"]*"[^>]*>\s*PASS\s*</span>', html, re.IGNORECASE))
        fail_steps = len(re.findall(r'<td>\s*<span[^>]*class="[^"]*(?:status-fail|fail-bg)[^"]*"[^>]*>\s*FAIL\s*</span>', html, re.IGNORECASE))
        warn_steps = len(re.findall(r'<td>\s*<span[^>]*class="[^"]*(?:status-warn|warn-bg)[^"]*"[^>]*>\s*WARNING\s*</span>', html, re.IGNORECASE))
        info_steps = len(re.findall(r'<td>\s*<span[^>]*class="[^"]*(?:status-info|info-bg)[^"]*"[^>]*>\s*INFO\s*</span>', html, re.IGNORECASE))

        total_steps = pass_steps + fail_steps + warn_steps + info_steps
        eval_steps = pass_steps + fail_steps

        if eval_steps > 0:
            pass_percentage = round((pass_steps / eval_steps) * 100, 1)
        elif total_steps > 0:
            pass_percentage = round((pass_steps / total_steps) * 100, 1)
        else:
            pass_percentage = 100.0 if fail_steps == 0 else 0.0

        overall_status = "PASSED" if fail_steps == 0 else "FAILED"

        return {
            "fileName": os.path.basename(file_path),
            "totalTestCases": max(len(flat_test_names), 1),
            "passed": pass_steps,
            "failed": fail_steps,
            "skipped": warn_steps + info_steps,
            "passPercentage": pass_percentage,
            "testCaseNames": flat_test_names,
            "overallStatus": overall_status
        }



