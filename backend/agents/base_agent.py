"""
Base Agent — Shared FIS logic and common agent interface.
All 4 agents inherit from this.
"""
from typing import List, Dict, Any
from datetime import datetime
from backend.models.finding import Finding, FindingCreate
from backend.models.fis import FinancialImpactStatement
from backend.config import APPROVAL_TIERS


class BaseAgent:
    """Base class for all CostIQ agents."""
    
    AGENT_TYPE = "base"
    AGENT_NAME = "Base Agent"
    AGENT_COLOR = "#e4a4bd"
    
    def __init__(self):
        self.findings: List[Finding] = []
    
    async def analyze(self, data: dict) -> List[Finding]:
        """Override in subclasses. Analyze data and return findings."""
        raise NotImplementedError
    
    def create_finding(self, 
                       finding_type: str,
                       title: str,
                       description: str,
                       severity: str,
                       baseline_cost: float,
                       projected_savings: float,
                       annualized_savings: float,
                       confidence_score: float,
                       formula: str,
                       intervention_cost: float = 0.0,
                       action_description: str = "",
                       data_sources: List[str] = None,
                       payback_period: str = "immediate",
                       run_id: str = "") -> Finding:
        """Create a Finding with a properly constructed FIS."""
        
        fis = FinancialImpactStatement(
            baseline_cost=baseline_cost,
            intervention_cost=intervention_cost,
            projected_savings=projected_savings,
            annualized_savings=annualized_savings,
            confidence_score=confidence_score,
            formula=formula,
            payback_period=payback_period,
            audit_trail=data_sources or [],
        )
        
        finding = Finding(
            run_id=run_id,
            agent_type=self.AGENT_TYPE,
            finding_type=finding_type,
            title=title,
            description=description,
            severity=severity,
            fis=fis,
            fis_json=fis.model_dump(),
            action_description=action_description,
            data_sources=data_sources or [],
        )
        
        self.findings.append(finding)
        return finding
    
    @staticmethod
    def route_approval(projected_savings: float) -> dict:
        """Route to correct approval tier based on financial impact."""
        for tier_name, config in sorted(
            APPROVAL_TIERS.items(), key=lambda x: x[1]["threshold"]
        ):
            if projected_savings <= config["threshold"]:
                return {
                    "tier": tier_name,
                    "approvers": config["approvers"],
                    "auto": len(config["approvers"]) == 0,
                }
        return {"tier": "c_suite", "approvers": ["cfo", "ceo"], "auto": False}
    
    @staticmethod
    def calculate_z_scores(amounts: List[float]) -> List[dict]:
        """Z-score anomaly detection on a list of amounts."""
        if len(amounts) < 3:
            return []
        
        mean = sum(amounts) / len(amounts)
        std = (sum((x - mean) ** 2 for x in amounts) / len(amounts)) ** 0.5
        
        anomalies = []
        for i, amount in enumerate(amounts):
            z_score = abs(amount - mean) / (std + 0.001)
            if z_score > 2.0:
                anomalies.append({
                    "index": i,
                    "amount": amount,
                    "z_score": z_score,
                    "expected": mean,
                    "deviation": amount - mean,
                })
        
        return anomalies
