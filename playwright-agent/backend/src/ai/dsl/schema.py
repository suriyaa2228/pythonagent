"""
Structured Test DSL Schema
==========================
Defines the Pydantic data models for the intermediate Test DSL as mandated by
Section 10 of the Target Architecture Specification.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DSLStep(BaseModel):
    page: str = Field(..., description="Target Page Object class name (e.g., 'HomePage', 'CartPage')")
    action: str = Field(..., description="Method name to call on Page Object (e.g., 'click_checkout')")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Named parameters to pass to the action method")


class DSLAssertion(BaseModel):
    page: str = Field(..., description="Target Page Object class or locator context")
    condition: str = Field(..., description="Condition or property to assert (e.g., 'order_summary_visible')")
    expected_value: Optional[Any] = Field(None, description="Optional expected value for comparison")


class StructuredTestDSL(BaseModel):
    test_id: str = Field(..., description="Test Case ID (e.g., 'TC026')")
    name: str = Field(..., description="Descriptive test name")
    description: Optional[str] = Field(None, description="Detailed use case description")
    preconditions: List[str] = Field(default_factory=list, description="List of required preconditions")
    steps: List[DSLStep] = Field(..., description="Ordered list of action steps")
    assertions: List[DSLAssertion] = Field(default_factory=list, description="Required assertions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Traceability and metadata")
