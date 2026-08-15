from pydantic import BaseModel
from typing import Optional


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
