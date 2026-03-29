"""
CostIQ API — FastAPI main application.
Real-time WebSocket feed, REST endpoints, CORS.
"""
import asyncio
import json
import uuid
from typing import Dict, List, Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.db.database import db
from backend.agents.orchestrator import orchestrator
from backend.scripts.generate_demo_data import generate_demo_data
from backend.config import CORS_ORIGINS


# ─── WebSocket Manager ───────────────────────────────────────────────
class WebSocketManager:
    """Manages WebSocket connections for real-time agent activity streaming."""

    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "global"):
        await websocket.accept()
        if channel not in self.connections:
            self.connections[channel] = set()
        self.connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "global"):
        if channel in self.connections:
            self.connections[channel].discard(websocket)

    async def broadcast(self, channel: str, data: dict):
        """Broadcast message to all connections on a channel."""
        if channel in self.connections:
            dead = set()
            for ws in self.connections[channel]:
                try:
                    await ws.send_json(data)
                except Exception:
                    dead.add(ws)
            self.connections[channel] -= dead
        # Also broadcast to global channel
        if "global" in self.connections and channel != "global":
            dead = set()
            for ws in self.connections["global"]:
                try:
                    await ws.send_json(data)
                except Exception:
                    dead.add(ws)
            self.connections["global"] -= dead


ws_manager = WebSocketManager()


# ─── Application Lifespan ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await db.connect()
    orchestrator.set_broadcast(ws_manager.broadcast)
    yield
    await db.disconnect()


# ─── FastAPI App ─────────────────────────────────────────────────────
app = FastAPI(
    title="CostIQ API",
    description="Enterprise Cost Intelligence & Autonomous Action Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request/Response Models ─────────────────────────────────────────
class AnalysisRequest(BaseModel):
    data_sources: List[str] = ["demo"]
    custom_data: dict = {}


class ApprovalDecisionRequest(BaseModel):
    decision: str  # approve, reject, modify
    notes: str = ""
    approver_id: str = "demo_user"


# ─── WebSocket Endpoint ──────────────────────────────────────────────
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "global"):
    await ws_manager.connect(websocket, channel)
    try:
        while True:
            # Keep alive — client can also send pings
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                # Echo back or handle client messages
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # Send keepalive
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)


# ─── Analysis Endpoints ──────────────────────────────────────────────
@app.post("/api/v1/analyze")
async def trigger_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Trigger full analysis with demo or custom data."""
    task_id = str(uuid.uuid4())

    # Use demo data if "demo" is in data sources
    if "demo" in request.data_sources:
        data = generate_demo_data()
    else:
        data = request.custom_data

    # Run analysis in background
    background_tasks.add_task(orchestrator.run_analysis, data, task_id)

    return {
        "task_id": task_id,
        "status": "initiated",
        "message": "Analysis started. Connect to WebSocket for real-time updates.",
        "ws_url": f"/ws/{task_id}",
    }


@app.get("/api/v1/analyze/{run_id}")
async def get_analysis_status(run_id: str):
    """Get analysis run status."""
    run = await db.get_run(run_id)
    if not run:
        return {"error": "Run not found"}
    
    findings = await db.get_findings_by_run(run_id)
    return {
        **run,
        "findings_count": len(findings),
        "findings_summary": [
            {
                "id": f.id,
                "agent_type": f.agent_type,
                "title": f.title,
                "savings": f.fis.projected_savings,
                "status": f.status,
            }
            for f in findings
        ],
    }


# ─── Findings Endpoints ──────────────────────────────────────────────
@app.get("/api/v1/findings")
async def list_findings():
    """List all findings."""
    findings = await db.get_all_findings()
    return {
        "findings": [
            {
                "id": f.id,
                "run_id": f.run_id,
                "agent_type": f.agent_type,
                "finding_type": f.finding_type,
                "title": f.title,
                "description": f.description,
                "severity": f.severity,
                "fis": f.fis.model_dump(),
                "action_description": f.action_description,
                "status": f.status,
                "created_at": f.created_at,
            }
            for f in findings
        ],
        "total": len(findings),
        "total_savings": sum(f.fis.projected_savings for f in findings),
    }


@app.get("/api/v1/findings/{finding_id}")
async def get_finding(finding_id: str):
    """Get a specific finding with full FIS."""
    finding = await db.get_finding(finding_id)
    if not finding:
        return {"error": "Finding not found"}
    
    approvals = await db.get_approvals_for_finding(finding_id)
    
    return {
        "id": finding.id,
        "run_id": finding.run_id,
        "agent_type": finding.agent_type,
        "finding_type": finding.finding_type,
        "title": finding.title,
        "description": finding.description,
        "severity": finding.severity,
        "fis": finding.fis.model_dump(),
        "action_description": finding.action_description,
        "data_sources": finding.data_sources,
        "status": finding.status,
        "created_at": finding.created_at,
        "approvals": [
            {
                "id": a.id,
                "tier": a.approval_tier,
                "decision": a.decision,
                "decided_by": a.decided_by,
                "notes": a.notes,
            }
            for a in approvals
        ],
    }


# ─── Approval Endpoints ──────────────────────────────────────────────
@app.get("/api/v1/approvals")
async def list_approvals():
    """List all pending approvals."""
    pending = await db.get_pending_approvals()
    result = []
    
    for approval in pending:
        finding = await db.get_finding(approval.finding_id)
        result.append({
            "approval_id": approval.id,
            "finding_id": approval.finding_id,
            "tier": approval.approval_tier,
            "required_approvers": approval.required_approvers,
            "decision": approval.decision,
            "created_at": approval.created_at,
            "finding": {
                "title": finding.title if finding else "Unknown",
                "agent_type": finding.agent_type if finding else "unknown",
                "savings": finding.fis.projected_savings if finding else 0,
                "severity": finding.severity if finding else "unknown",
            } if finding else None,
        })
    
    return {"approvals": result, "total_pending": len(result)}


@app.post("/api/v1/approvals/{approval_id}/respond")
async def respond_to_approval(approval_id: str, request: ApprovalDecisionRequest):
    """Human approver responds to an approval request."""
    approval = await db.get_approval(approval_id)
    if not approval:
        return {"error": "Approval not found"}

    updated = await db.update_approval(
        approval_id,
        decision=request.decision,
        decided_by=request.approver_id,
        notes=request.notes,
    )

    # Broadcast approval event
    finding = await db.get_finding(approval.finding_id)
    await ws_manager.broadcast("global", {
        "type": "approval_decision",
        "payload": {
            "approval_id": approval_id,
            "finding_id": approval.finding_id,
            "decision": request.decision,
            "finding_title": finding.title if finding else "Unknown",
            "savings": finding.fis.projected_savings if finding else 0,
        },
    })

    action_taken = ""
    if request.decision == "approve" and finding:
        action_taken = finding.action_description
        await db.update_finding_status(finding.id, "executed")

        # Broadcast execution event
        await ws_manager.broadcast("global", {
            "type": "agent_activity",
            "payload": {
                "agent": finding.agent_type,
                "action": f"Executing approved action",
                "detail": action_taken,
                "status": "executing",
            },
        })

        # Simulate execution delay
        await asyncio.sleep(1)

        await ws_manager.broadcast("global", {
            "type": "agent_activity",
            "payload": {
                "agent": finding.agent_type,
                "action": f"Action executed successfully",
                "detail": f"Saved ${finding.fis.projected_savings:,.0f}",
                "status": "completed",
            },
        })

    return {
        "id": approval_id,
        "finding_id": approval.finding_id,
        "decision": request.decision,
        "status": "executed" if request.decision == "approve" else request.decision,
        "message": f"Action {'executed' if request.decision == 'approve' else request.decision}: {action_taken}",
    }


# ─── Stats & Impact Board ────────────────────────────────────────────
@app.get("/api/v1/stats")
async def get_stats():
    """Get total savings statistics."""
    return await db.get_total_stats()


@app.get("/api/v1/activity")
async def get_activity(limit: int = 50):
    """Get recent agent activity."""
    activity = await db.get_recent_activity(limit)
    return {"activity": activity}


# ─── Connector Endpoints ─────────────────────────────────────────────
@app.get("/api/v1/connectors")
async def list_connectors():
    """List configured data connectors."""
    connectors = await db.get_connectors()
    
    # Default available connectors
    available = [
        {"id": "sap", "name": "SAP ERP", "type": "erp", "icon": "🏢", "status": "available", "description": "Procurement, finance, and HR data"},
        {"id": "salesforce", "name": "Salesforce", "type": "crm", "icon": "☁️", "status": "available", "description": "Customer and revenue data"},
        {"id": "aws", "name": "AWS Cost Explorer", "type": "cloud", "icon": "🔶", "status": "available", "description": "Cloud infrastructure costs and usage"},
        {"id": "jira", "name": "JIRA", "type": "project", "icon": "📋", "status": "available", "description": "Project tracking and SLA metrics"},
        {"id": "quickbooks", "name": "QuickBooks", "type": "finance", "icon": "📊", "status": "available", "description": "Financial transactions and reporting"},
        {"id": "csv", "name": "CSV Upload", "type": "file", "icon": "📄", "status": "available", "description": "Universal data import via CSV"},
    ]
    
    # Mark connected ones
    connected_ids = {c["id"] for c in connectors}
    for conn in available:
        if conn["id"] in connected_ids:
            conn["status"] = "connected"
    
    return {"connectors": available}


@app.post("/api/v1/connectors/{connector_id}/connect")
async def connect_connector(connector_id: str):
    """Connect a data source (demo mode)."""
    await db.save_connector(connector_id, {
        "type": connector_id,
        "mode": "demo",
    })
    
    await ws_manager.broadcast("global", {
        "type": "agent_activity",
        "payload": {
            "agent": "supervisor",
            "action": f"Connector activated",
            "detail": f"{connector_id.upper()} connected in demo mode — data ready for analysis",
            "status": "completed",
        },
    })
    
    return {"status": "connected", "connector_id": connector_id, "mode": "demo"}


@app.post("/api/v1/connectors/{connector_id}/disconnect")
async def disconnect_connector(connector_id: str):
    """Disconnect a data source."""
    return {"status": "disconnected", "connector_id": connector_id}


# ─── Health ───────────────────────────────────────────────────────────
@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "version": "1.0.0", "demo_mode": True}
