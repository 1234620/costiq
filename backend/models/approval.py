"""
Approval — Enterprise approval workflow models.
4-tier routing based on financial impact.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid


class ApprovalDecision(BaseModel):
    """Input model for approval response."""
    decision: Literal["approve", "reject", "modify"]
    notes: Optional[str] = None
    approver_id: str = "demo_user"


class ApprovalRequest(BaseModel):
    """An approval request awaiting human decision."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    finding_id: str
    approval_tier: str
    required_approvers: List[str] = Field(default_factory=list)
    decision: Literal["pending", "approved", "rejected"] = "pending"
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ApprovalResponse(BaseModel):
    """API response after approval decision."""
    id: str
    finding_id: str
    decision: str
    status: str
    message: str
