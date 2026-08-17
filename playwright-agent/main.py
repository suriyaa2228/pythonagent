import os
import sys

# Ensure src directory is in Python module search path
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import agent_routes, execution_routes, ai_generation_routes

# Ensure reports directory exists at startup
base_dir = os.path.dirname(os.path.abspath(__file__))
reports_dir = os.path.join(base_dir, "python_playwright", "reports")
os.makedirs(reports_dir, exist_ok=True)

app = FastAPI(title="Playwright Agent AI Platform", version="2.0.0")

app.include_router(agent_routes.router, prefix="/api/v1/agent", tags=["Agent"])
app.include_router(execution_routes.router, prefix="/api/v1/executions", tags=["Executions"])
app.include_router(ai_generation_routes.router, prefix="/api/v1/ai", tags=["AI Generation & Reports"])

# Mount static files and images
app.mount("/static", StaticFiles(directory="static"), name="static")

images_dir = os.path.join(reports_dir, "images")
os.makedirs(images_dir, exist_ok=True)
app.mount("/api/v1/reports/images", StaticFiles(directory=images_dir), name="report_images")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/api/v1/reports")
def list_reports():
    if not os.path.exists(reports_dir):
        return []
    files = [f for f in os.listdir(reports_dir) if f.startswith("extent_report_") and f.endswith(".html")]
    # sort by modification time descending
    files.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
    return files

@app.get("/api/v1/reports/{report_name}")
def get_report(report_name: str):
    report_path = os.path.join(reports_dir, report_name)
    if os.path.exists(report_path):
        return FileResponse(report_path)
    return {"error": "Report not found"}

@app.delete("/api/v1/reports/{report_name}")
def delete_report(report_name: str):
    report_path = os.path.join(reports_dir, report_name)
    if os.path.exists(report_path) and report_name.startswith("extent_report_"):
        try:
            os.remove(report_path)
            return {"status": "success", "message": "Report deleted"}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "Report not found or invalid"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
