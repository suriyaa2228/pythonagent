from pydantic import BaseModel
from typing import Optional, List


class ExecutionStatus(BaseModel):
    executionId: str
    testId: str
    status: str
    duration: Optional[float] = None
    artifacts: List[str] = []
