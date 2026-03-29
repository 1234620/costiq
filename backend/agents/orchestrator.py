"""
CostIQ Orchestrator — Coordinates all 4 agents, manages state, and handles
the analysis pipeline. Simplified version for hackathon (no LangGraph dependency).

Flow:
1. Receive data from connectors
2. Route to appropriate agents based on data type
3. Collect findings with FIS
4. Route to approval workflow
5. Execute approved actions
6. Synthesize final report
"""
import asyncio
import uuid
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from backend.agents.spend_agent import SpendAgent
from backend.agents.sla_agent import SLAAgent
from backend.agents.resource_agent import ResourceAgent
from backend.agents.finops_agent import FinOpsAgent
from backend.models.finding import Finding
from backend.models.approval import ApprovalRequest
from backend.db.database import db
from backend.config import APPROVAL_TIERS


class CostIQOrchestrator:
    """
    Supervisor agent that orchestrates all 4 CostIQ agents.
    Manages the analysis pipeline with human-in-the-loop approval gates.
    """

    def __init__(self):
        self.spend_agent = SpendAgent()
        self.sla_agent = SLAAgent()
        self.resource_agent = ResourceAgent()
        self.finops_agent = FinOpsAgent()
        self._broadcast: Optional[Callable] = None

    def set_broadcast(self, broadcast_fn: Callable):
        """Set WebSocket broadcast function for real-time updates."""
        self._broadcast = broadcast_fn

    async def _emit(self, run_id: str, event_type: str, payload: dict):
        """Emit event to WebSocket and log activity."""
        activity = {
            "run_id": run_id,
            "type": event_type,
            **payload,
        }
        await db.log_activity(activity)
        if self._broadcast:
            try:
                await self._broadcast(run_id, {"type": event_type, "payload": payload})
            except Exception:
                pass

    async def run_analysis(self, data: dict, run_id: str = None) -> dict:
        """
        Main entry point. Runs all applicable agents on the provided data.
        Returns a synthesis report with all findings.
        """
        if not run_id:
            run_id = str(uuid.uuid4())

        await db.create_run(run_id)
        await db.update_run(run_id, status="running")

        await self._emit(run_id, "agent_activity", {
            "agent": "supervisor",
            "action": "Analysis initiated",
            "detail": f"Processing data from {len(data.get('data_sources', ['manual']))} sources",
            "status": "running",
        })

        all_findings: List[Finding] = []

        # Route to agents based on available data
        agents_to_run = []

        if data.get("invoices") or data.get("contracts"):
            agents_to_run.append(("spend", self.spend_agent, {
                "invoices": data.get("invoices", []),
                "contracts": data.get("contracts", {}),
                "run_id": run_id,
            }))

        if data.get("sla_configs") or data.get("queue_metrics"):
            agents_to_run.append(("sla", self.sla_agent, {
                "sla_configs": data.get("sla_configs", []),
                "queue_metrics": data.get("queue_metrics", []),
                "contracts": data.get("sla_contracts", {}),
                "run_id": run_id,
            }))

        if data.get("cloud_instances") or data.get("saas_apps") or data.get("on_demand_monthly_spend"):
            agents_to_run.append(("resource", self.resource_agent, {
                "cloud_instances": data.get("cloud_instances", []),
                "saas_apps": data.get("saas_apps", []),
                "on_demand_monthly_spend": data.get("on_demand_monthly_spend", 0),
                "run_id": run_id,
            }))

        if data.get("budget_vs_actual") or data.get("transactions") or data.get("accruals"):
            agents_to_run.append(("finops", self.finops_agent, {
                "budget_vs_actual": data.get("budget_vs_actual", []),
                "transactions": data.get("transactions", []),
                "accruals": data.get("accruals", []),
                "run_id": run_id,
            }))

        # Run agents sequentially with real-time updates
        for agent_type, agent, agent_data in agents_to_run:
            await self._emit(run_id, "agent_activity", {
                "agent": agent_type,
                "action": f"{agent.AGENT_NAME} starting analysis",
                "detail": f"Processing {agent_type} data...",
                "status": "running",
            })

            # Add a small delay for dramatic effect in demo
            await asyncio.sleep(0.5)

            try:
                findings = await agent.analyze(agent_data)

                for finding in findings:
                    await db.save_finding(finding)

                    # Emit each finding as it's discovered
                    await self._emit(run_id, "finding", {
                        "agent": agent_type,
                        "finding_id": finding.id,
                        "title": finding.title,
                        "savings": finding.fis.projected_savings,
                        "severity": finding.severity,
                        "confidence": finding.fis.confidence_score,
                    })

                    await asyncio.sleep(0.3)  # Stagger findings for visual effect

                all_findings.extend(findings)

                await self._emit(run_id, "agent_activity", {
                    "agent": agent_type,
                    "action": f"{agent.AGENT_NAME} completed",
                    "detail": f"Found {len(findings)} cost savings opportunities",
                    "status": "completed",
                    "findings_count": len(findings),
                })

            except Exception as e:
                await self._emit(run_id, "agent_activity", {
                    "agent": agent_type,
                    "action": f"{agent.AGENT_NAME} error",
                    "detail": str(e),
                    "status": "error",
                })

        # Create approval requests for significant findings
        for finding in all_findings:
            routing = finding.fis.projected_savings
            tier_info = self.spend_agent.route_approval(routing)

            if not tier_info["auto"]:
                approval = ApprovalRequest(
                    finding_id=finding.id,
                    approval_tier=tier_info["tier"],
                    required_approvers=tier_info["approvers"],
                )
                await db.create_approval(approval)

        # Synthesis
        total_identified = sum(f.fis.projected_savings for f in all_findings)
        total_annualized = sum(f.fis.annualized_savings for f in all_findings)

        await db.update_run(
            run_id,
            status="completed",
            total_savings_identified=total_identified,
            completed_at=datetime.now().isoformat(),
        )

        await self._emit(run_id, "agent_activity", {
            "agent": "supervisor",
            "action": "Analysis complete",
            "detail": (
                f"Total: {len(all_findings)} findings, "
                f"${total_identified:,.0f} identified savings, "
                f"${total_annualized:,.0f} annualized"
            ),
            "status": "completed",
        })

        return {
            "run_id": run_id,
            "status": "completed",
            "total_findings": len(all_findings),
            "total_savings_identified": total_identified,
            "total_annualized_savings": total_annualized,
            "findings_by_agent": {
                agent_type: {
                    "count": len([f for f in all_findings if f.agent_type == agent_type]),
                    "savings": sum(f.fis.projected_savings for f in all_findings if f.agent_type == agent_type),
                }
                for agent_type in ["spend", "sla", "resource", "finops"]
            },
            "pending_approvals": len(await db.get_pending_approvals()),
        }


# Global orchestrator instance
orchestrator = CostIQOrchestrator()
