"""
Finding — A cost leakage discovery made by an agent.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid

from .fis import FinancialImpactStatement


class FindingCreate(BaseModel):
    """Input model for creating a finding."""
    agent_type: Literal["spend", "sla", "resource", "finops"]
    finding_type: str
    title: str
    description: str
    severity: Literal["critical", "high", "medium", "low"] = "medium"
    fis: FinancialImpactStatement
    action_description: str = ""
    data_sources: List[str] = Field(default_factory=list)


class Finding(BaseModel):
    """Full finding model with ID and metadata."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = ""
    agent_type: Literal["spend", "sla", "resource", "finops"]
    finding_type: str
    title: str
    description: str
    severity: Literal["critical", "high", "medium", "low"] = "medium"
    fis: FinancialImpactStatement
    fis_json: Optional[dict] = None
    action_description: str = ""
    data_sources: List[str] = Field(default_factory=list)
    status: Literal["open", "approved", "rejected", "executed"] = "open"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class FindingResponse(BaseModel):
    """API response model."""
    id: str
    agent_type: str
    finding_type: str
    title: str
    description: str
    severity: str
    fis: FinancialImpactStatement
    action_description: str
    status: str
    created_at: str
