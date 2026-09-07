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

from agents.planner_agent import PlaywrightPlanner
from agents.generator_agent import PlaywrightGenerator
from agents.healer_agent import PlaywrightHealer
from agent.mcp.playwright_mcp_adapter import PlaywrightMcpAdapter
from agent.registry.test_case_repository import TestCaseRepository
from agent.registry.test_registry import TestRegistry
from models.task import SaveTestCaseRequest, McpRegressionRequest

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

# Initialize Agents & Repositories
planner_agent = PlaywrightPlanner(orchestrator)
generator_agent = PlaywrightGenerator(orchestrator)
healer_agent = PlaywrightHealer(orchestrator)
mcp_adapter = PlaywrightMcpAdapter()
test_repository = TestCaseRepository(agent_dir)
test_registry = TestRegistry()


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


class PlannerDraftRequest(BaseModel):
    useCase: str
    acceptanceCriteria: List[str]
    project: Optional[str] = "playwright"
    environment: Optional[str] = "stage"


class HealerHealRequest(BaseModel):
    failedScript: str
    errorMessage: str
    domDumpPath: Optional[str] = None
    screenshotPath: Optional[str] = None


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

    result = generator_agent.generate_script(
        user_story=request.userStory,
        acceptance_criteria=request.acceptanceCriteria,
        project=request.project or "playwright",
        environment=request.environment or "stage"
    )
    return result


@router.post("/planner/draft")
async def draft_test_plan(request: PlannerDraftRequest):
    """Planner Agent: Drafts structured test cases and steps from user requirements."""
    if not request.useCase.strip():
        raise HTTPException(status_code=400, detail="Use case description is required.")

    result = planner_agent.draft_test_plan(
        use_case=request.useCase,
        acceptance_criteria=request.acceptanceCriteria,
        project=request.project or "playwright",
        environment=request.environment or "stage"
    )
    return result


@router.post("/healer/heal")
async def heal_test_script(request: HealerHealRequest):
    """Healer Agent: Analyzes execution stack traces and DOM dumps to auto-repair broken scripts."""
    if not request.failedScript.strip() or not request.errorMessage.strip():
        raise HTTPException(status_code=400, detail="failedScript and errorMessage are required.")

    result = healer_agent.heal_script(
        failed_script=request.failedScript,
        error_message=request.errorMessage,
        dom_dump_path=request.domDumpPath,
        screenshot_path=request.screenshotPath
    )
    return result


@router.post("/save-test-case")
async def save_test_case(request: SaveTestCaseRequest):
    """Persists generated Python test script to python_playwright/tests and registers metadata."""
    if not request.testCaseNumber.strip() or not request.testCaseName.strip() or not request.pythonScript.strip():
        raise HTTPException(status_code=400, detail="testCaseNumber, testCaseName, and pythonScript are mandatory.")

    try:
        res = test_repository.save_test_case(request)
        return {
            "success": True,
            "message": f"Test case {request.testCaseNumber} saved successfully.",
            "testCase": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/execute-regression")
def execute_mcp_regression(request: McpRegressionRequest):
    """Executes regression test batch using Playwright MCP tool tracing and live telemetry."""
    if not request.testCaseIds:
        raise HTTPException(status_code=400, detail="testCaseIds list is required.")

    test_infos = []
    for t_id in request.testCaseIds:
        info = test_registry.get_test(t_id)
        if info:
            test_infos.append({"testId": t_id, "name": info.get("name", t_id), "path": info.get("path", "")})

    if not test_infos:
        raise HTTPException(status_code=404, detail="No matching tests found in registry.")

    try:
        res = mcp_adapter.run_agentic_regression(
            test_infos=test_infos,
            environment=request.environment or "stage",
            headless=request.headless if request.headless is not None else False
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP Regression Execution Error: {str(e)}")




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
    total_passed = 0
    total_failed = 0

    for r in report_files:
        summary = extent_parser.parse_report_file(r["filePath"])
        if summary.get("overallStatus") == "PASSED":
            total_passed += 1
        else:
            total_failed += 1
        summaries.append({**r, **summary})

    total_count = len(report_files)
    avg_pass_rate = round((total_passed / total_count) * 100, 1) if total_count > 0 else 100.0

    return {
        "totalReports": total_count,
        "totalPassed": total_passed,
        "totalFailed": total_failed,
        "averagePassRate": avg_pass_rate,
        "reports": summaries
    }


