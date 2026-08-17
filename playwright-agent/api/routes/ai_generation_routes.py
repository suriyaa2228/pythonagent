"""
AI Test Generation & Modification Routes
=========================================
Exposes the LangChain + Groq + RAG test generation pipeline, AI chat modification,
AST validation, and Extent Report aggregation endpoints.
"""

import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from discovery.framework_scanner import FrameworkScanner
from generation.orchestrator import GenerationOrchestrator
from generation.validator import FrameworkValidator
from moderation.moderator import ContentModerator
from rag.ingestion_pipeline import RAGIngestionPipeline
from execution.runner import TestRunner
from reports.extent_parser import ExtentReportParser

router = APIRouter()

# Initialize core services
agent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
playwright_dir = os.path.join(agent_dir, "python_playwright")
reports_dir = os.path.join(playwright_dir, "reports")

scanner = FrameworkScanner(playwright_dir)
symbol_registry = scanner.scan_all()

moderator = ContentModerator()
rag_pipeline = RAGIngestionPipeline(playwright_dir, moderator=moderator)
rag_pipeline.ingest_directory(["pages", "fixtures", "utils", "config"])

orchestrator = GenerationOrchestrator(
    rag_pipeline=rag_pipeline,
    symbol_registry=symbol_registry
)
validator = FrameworkValidator(symbol_registry)
runner = TestRunner(agent_dir)
extent_parser = ExtentReportParser(reports_dir)


class GenerateTestRequest(BaseModel):
    userStory: str
    acceptanceCriteria: List[str]
    project: Optional[str] = "playwright"
    environment: Optional[str] = "stage"


class ModifyTestRequest(BaseModel):
    currentScript: str
    message: str


class ValidateScriptRequest(BaseModel):
    pythonScript: str
    acceptanceCriteria: Optional[List[str]] = None


class ModerateRequest(BaseModel):
    content: str


class RagRetrieveRequest(BaseModel):
    query: str
    topK: Optional[int] = 5
    scoreThreshold: Optional[float] = 0.0


class ExecuteScriptRequest(BaseModel):
    pythonScript: str
    testName: Optional[str] = "test_generated_tc.py"
    environment: Optional[str] = "stage"
    headless: Optional[bool] = True


@router.post("/moderate")
async def moderate_content(request: ModerateRequest):
    """Runs pre-embedding rule-based security moderation and sensitive data masking."""
    res = moderator.moderate_and_sanitize(request.content)
    return res.to_dict()


@router.post("/rag/retrieve")
async def retrieve_rag_context(request: RagRetrieveRequest):
    """Retrieves relevant framework AST chunks via vector similarity search."""
    results = rag_pipeline.retrieve_context(
        query=request.query,
        top_k=request.topK or 5,
        score_threshold=request.scoreThreshold or 0.0
    )
    return {
        "query": request.query,
        "resultsCount": len(results),
        "results": results
    }


@router.get("/symbols")
async def get_symbol_registry():
    """Returns the full discovered framework symbol registry."""
    return symbol_registry


@router.post("/generate")
async def generate_test(request: GenerateTestRequest):
    """Generates an automated test script from user story and acceptance criteria."""
    if not request.userStory.strip():
        raise HTTPException(status_code=400, detail="User story is required.")

    result = orchestrator.generate_test_script(
        user_story=request.userStory,
        acceptance_criteria=request.acceptanceCriteria,
        project=request.project or "playwright",
        environment=request.environment or "stage"
    )
    return result


@router.post("/modify")
async def modify_test(request: ModifyTestRequest):
    """Modifies a generated script conversationally via AI chat."""
    if not request.currentScript.strip() or not request.message.strip():
        raise HTTPException(status_code=400, detail="Script and message are required.")

    result = orchestrator.modify_test_script(
        current_script=request.currentScript,
        modification_request=request.message
    )
    return result


@router.post("/validate")
async def validate_script(request: ValidateScriptRequest):
    """Validates Python AST, framework compliance, and acceptance criteria coverage."""
    res = validator.validate_script(request.pythonScript, request.acceptanceCriteria)
    return res.to_dict()


@router.post("/execute")
async def execute_test(request: ExecuteScriptRequest):
    """Executes a generated Python test script in an isolated subprocess workspace."""
    # First validate script
    val = validator.validate_script(request.pythonScript)
    if not val.is_valid:
        raise HTTPException(status_code=400, detail={"message": "Script failed validation", "errors": val.errors})

    result = runner.execute_script(
        python_script=request.pythonScript,
        test_name=request.testName or "test_generated_tc.py",
        headless=request.headless if request.headless is not None else True,
        env_name=request.environment or "stage"
    )
    return result.to_dict()


@router.get("/reports/summary")
async def get_reports_summary():
    """Aggregates all Extent Report statistics for the dashboard."""
    report_files = extent_parser.list_reports()
    summaries = []
    for r in report_files[:10]:
        summary = extent_parser.parse_report_file(r["filePath"])
        summaries.append({**r, **summary})
    return {
        "totalReports": len(report_files),
        "reports": summaries
    }
