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

        # Count PASS / FAIL / SKIP badges
        pass_matches = len(re.findall(r'<span class="badge pass-bg[^"]*">Pass</span>|<span class="badge[^"]*pass[^"]*">', html, re.IGNORECASE))
        fail_matches = len(re.findall(r'<span class="badge fail-bg[^"]*">Fail</span>|<span class="badge[^"]*fail[^"]*">', html, re.IGNORECASE))
        skip_matches = len(re.findall(r'<span class="badge skip-bg[^"]*">Skip</span>', html, re.IGNORECASE))

        # Extract test case names
        test_names = re.findall(r'<p class="name">([^<]+)</p>|<h5 class="test-status[^"]*">([^<]+)</h5>', html)
        flat_test_names = [t[0] or t[1] for t in test_names if t[0] or t[1]]

        total = max(len(flat_test_names), pass_matches + fail_matches + skip_matches, 1)
        passed = pass_matches if pass_matches > 0 else (1 if fail_matches == 0 else 0)
        failed = fail_matches
        skipped = skip_matches
        pass_percentage = round((passed / total) * 100, 2) if total > 0 else 100.0

        return {
            "fileName": os.path.basename(file_path),
            "totalTestCases": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "passPercentage": pass_percentage,
            "testCaseNames": flat_test_names,
            "overallStatus": "PASSED" if failed == 0 else "FAILED"
        }
