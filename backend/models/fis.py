"""
Financial Impact Statement (FIS) — The core data model.
Every agent action MUST produce one of these.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class FinancialImpactStatement(BaseModel):
    """
    The Financial Impact Statement is CostIQ's signature output.
    Every number must be backed by a formula and audit trail.
    """
    baseline_cost: float = Field(..., description="What you were spending (documented)")
    intervention_cost: float = Field(0.0, description="Cost of the intervention itself")
    projected_savings: float = Field(..., description="Dollar amount saved")
    annualized_savings: float = Field(..., description="Projected over 12 months")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Data quality confidence 0-1")
    formula: str = Field(..., description="Human-readable formula showing the math")
    payback_period: str = Field("immediate", description="How quickly savings materialize")
    audit_trail: List[str] = Field(default_factory=list, description="Every data source used")
    
    # Extended fields  
    baseline_period: str = Field("12 months", description="Reference period for baseline")
    currency: str = Field("USD", description="Currency code")
    notes: Optional[str] = None

    @property
    def roi(self) -> float:
        """Return on investment for the intervention."""
        if self.intervention_cost == 0:
            return float('inf')
        return (self.projected_savings - self.intervention_cost) / self.intervention_cost

    @property
    def net_savings(self) -> float:
        """Savings minus intervention cost."""
        return self.projected_savings - self.intervention_cost

    def summary_text(self) -> str:
        """Board-ready summary string."""
        return (
            f"Baseline: ${self.baseline_cost:,.0f} | "
            f"Savings: ${self.projected_savings:,.0f} | "
            f"Confidence: {self.confidence_score:.0%} | "
            f"Formula: {self.formula}"
        )
