from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AgentTaskRequest(BaseModel):
    action: str
    testId: Optional[str] = None
    testIds: Optional[list[str]] = None
    environment: Optional[str] = "default"

class AgentTaskResponse(BaseModel):
    taskId: str
    executionId: str
    status: str

class AgentTestInfo(BaseModel):
    testId: str
    name: str
    path: str
    enabled: bool

class AgentTestListResponse(BaseModel):
    tests: list[AgentTestInfo]


class TestCaseMetadata(BaseModel):
    author: Optional[str] = "AI_Agent"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: List[str] = []
    environment: Optional[str] = "stage"
    execution_mode: Optional[str] = "PYTEST"


class TestCaseModel(BaseModel):
    id: str
    number: str
    name: str
    status: str = "SAVED"
    scripts: Dict[str, str] = {}
    metadata: Optional[TestCaseMetadata] = None


class SaveTestCaseRequest(BaseModel):
    testCaseNumber: str
    testCaseName: str
    pythonScript: str
    userStory: Optional[str] = None
    environment: Optional[str] = "stage"


class SaveTestCaseResponse(BaseModel):
    success: bool
    message: str
    testCase: Optional[Dict[str, Any]] = None


class McpRegressionRequest(BaseModel):
    testCaseIds: List[str]
    environment: Optional[str] = "stage"
    enableLiveHealing: Optional[bool] = True
    headless: Optional[bool] = False


