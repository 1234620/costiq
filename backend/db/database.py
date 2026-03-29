"""
Database layer — SQLite async engine with in-memory store for hackathon speed.
"""
import json
from typing import List, Optional, Dict
from datetime import datetime
from backend.models.finding import Finding
from backend.models.approval import ApprovalRequest


class InMemoryDB:
    """
    In-memory database for hackathon demo.
    Stores findings, approvals, and analysis runs.
    Production would use PostgreSQL.
    """
    
    def __init__(self):
        self.findings: Dict[str, Finding] = {}
        self.approvals: Dict[str, ApprovalRequest] = {}
        self.runs: Dict[str, dict] = {}
        self.agent_activity: List[dict] = []
        self.connector_configs: Dict[str, dict] = {}
    
    async def connect(self):
        """Initialize (no-op for in-memory)."""
        pass
    
    async def disconnect(self):
        """Cleanup (no-op for in-memory)."""
        pass
    
    # --- Analysis Runs ---
    
    async def create_run(self, run_id: str, initiated_by: str = "demo_user") -> dict:
        run = {
            "id": run_id,
            "status": "initiated",
            "total_savings_identified": 0.0,
            "total_savings_approved": 0.0,
            "total_savings_executed": 0.0,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "initiated_by": initiated_by,
        }
        self.runs[run_id] = run
        return run
    
    async def update_run(self, run_id: str, **kwargs) -> dict:
        if run_id in self.runs:
            self.runs[run_id].update(kwargs)
        return self.runs.get(run_id, {})
    
    async def get_run(self, run_id: str) -> Optional[dict]:
        return self.runs.get(run_id)
    
    async def get_all_runs(self) -> List[dict]:
        return list(self.runs.values())
    
    # --- Findings ---
    
    async def save_finding(self, finding: Finding) -> Finding:
        self.findings[finding.id] = finding
        # Update run savings
        if finding.run_id and finding.run_id in self.runs:
            self.runs[finding.run_id]["total_savings_identified"] += finding.fis.projected_savings
        return finding
    
    async def get_finding(self, finding_id: str) -> Optional[Finding]:
        return self.findings.get(finding_id)
    
    async def get_findings_by_run(self, run_id: str) -> List[Finding]:
        return [f for f in self.findings.values() if f.run_id == run_id]
    
    async def get_all_findings(self) -> List[Finding]:
        return sorted(self.findings.values(), key=lambda f: f.created_at, reverse=True)
    
    async def update_finding_status(self, finding_id: str, status: str) -> Optional[Finding]:
        if finding_id in self.findings:
            self.findings[finding_id].status = status
        return self.findings.get(finding_id)
    
    # --- Approvals ---
    
    async def create_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        self.approvals[approval.id] = approval
        return approval
    
    async def get_approval(self, approval_id: str) -> Optional[ApprovalRequest]:
        return self.approvals.get(approval_id)
    
    async def get_approvals_for_finding(self, finding_id: str) -> List[ApprovalRequest]:
        return [a for a in self.approvals.values() if a.finding_id == finding_id]
    
    async def get_pending_approvals(self) -> List[ApprovalRequest]:
        return [a for a in self.approvals.values() if a.decision == "pending"]
    
    async def update_approval(self, approval_id: str, decision: str, 
                               decided_by: str, notes: str = None) -> Optional[ApprovalRequest]:
        if approval_id in self.approvals:
            self.approvals[approval_id].decision = decision
            self.approvals[approval_id].decided_by = decided_by
            self.approvals[approval_id].decided_at = datetime.now().isoformat()
            self.approvals[approval_id].notes = notes
            
            # Update finding status
            finding_id = self.approvals[approval_id].finding_id
            if decision == "approved":
                await self.update_finding_status(finding_id, "approved")
            elif decision == "rejected":
                await self.update_finding_status(finding_id, "rejected")
        
        return self.approvals.get(approval_id)
    
    # --- Agent Activity ---
    
    async def log_activity(self, activity: dict):
        activity["timestamp"] = datetime.now().isoformat()
        self.agent_activity.insert(0, activity)
        # Keep last 200 entries
        self.agent_activity = self.agent_activity[:200]
    
    async def get_recent_activity(self, limit: int = 50) -> List[dict]:
        return self.agent_activity[:limit]
    
    # --- Connectors ---
    
    async def save_connector(self, connector_id: str, config: dict):
        self.connector_configs[connector_id] = {
            **config,
            "id": connector_id,
            "last_sync": datetime.now().isoformat(),
            "is_active": True,
        }
    
    async def get_connectors(self) -> List[dict]:
        return list(self.connector_configs.values())
    
    # --- Stats ---
    
    async def get_total_stats(self) -> dict:
        findings = list(self.findings.values())
        return {
            "total_findings": len(findings),
            "total_identified": sum(f.fis.projected_savings for f in findings),
            "total_approved": sum(f.fis.projected_savings for f in findings if f.status in ("approved", "executed")),
            "total_executed": sum(f.fis.projected_savings for f in findings if f.status == "executed"),
            "by_agent": {
                agent: {
                    "count": len([f for f in findings if f.agent_type == agent]),
                    "savings": sum(f.fis.projected_savings for f in findings if f.agent_type == agent)
                }
                for agent in ["spend", "sla", "resource", "finops"]
            },
            "by_severity": {
                sev: len([f for f in findings if f.severity == sev])
                for sev in ["critical", "high", "medium", "low"]
            }
        }


# Global instance
db = InMemoryDB()
