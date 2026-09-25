"""
Reports Routes
==============
Provides API endpoints for Extent & HTML report summary and listing.
"""

import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()
reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "python_playwright", "reports"))


@router.get("/")
def list_reports():
    if not os.path.exists(reports_dir):
        return []
    files = [f for f in os.listdir(reports_dir) if f.startswith("extent_report_") and f.endswith(".html")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
    return files


@router.get("/summary")
def get_reports_summary():
    if not os.path.exists(reports_dir):
        return {"total_reports": 0, "latest_report": None}
    files = [f for f in os.listdir(reports_dir) if f.startswith("extent_report_") and f.endswith(".html")]
    return {
        "total_reports": len(files),
        "latest_report": files[0] if files else None
    }
