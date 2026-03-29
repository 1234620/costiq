# 🏆 CostIQ — AI for Enterprise Cost Intelligence & Autonomous Action

> *"Every enterprise leaks money. CostIQ is the first autonomous system that doesn't just find those leaks — it plugs them."*

![CostIQ](https://img.shields.io/badge/CostIQ-Enterprise%20AI-e4a4bd?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge)

---

## 🎯 What is CostIQ?

CostIQ is an **autonomous AI cost intelligence platform** with 4 specialized agents that continuously monitor procurement, SLAs, resource utilization, and financial operations — then **take corrective action** with board-ready math on every dollar saved.

### The Agents

| Agent | Mission | Example Finding |
|-------|---------|-----------------|
| 💰 **Spend Intelligence** | Duplicate invoices, rate creep, vendor overcharges | "Acme invoiced $55,860/mo vs contracted $42,000 for 18 months — **$249K overcharge**" |
| ⚡ **SLA Prevention** | Predict SLA breaches before they happen | "73% breach probability, $182K exposure. Reroute 200 tickets for $800 → **170× ROI**" |
| ☁️ **Resource Optimization** | Cloud rightsizing, SaaS license waste | "23 EC2 instances at <30% CPU — **$87K/year waste**" |
| 📊 **Financial Operations** | Variance analysis, reconciliation | "Marketing budget +15.5% variance, volume-driven — **$340K correctable**" |

### The Differentiator: Financial Impact Statements (FIS)

Every finding produces a **Financial Impact Statement** with:
- ✅ Baseline cost (documented)
- ✅ Projected savings with **explicit formula**
- ✅ Confidence score (0-1)
- ✅ Complete audit trail
- ✅ Intervention ROI

*No savings number without a formula. That's how you pass the CFO test.*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    COSTIQ PLATFORM                      │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │          FRONTEND (Next.js 14 + TypeScript)       │  │
│  │  Dark Luxury UI · Fluid Background · Stepper UI   │  │
│  └────────────────────┬──────────────────────────────┘  │
│                       │ REST + WebSocket                 │
│  ┌────────────────────▼──────────────────────────────┐  │
│  │              API GATEWAY (FastAPI)                 │  │
│  │  CORS · WebSocket Manager · Background Tasks      │  │
│  └────────────────────┬──────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────▼──────────────────────────────┐  │
│  │            ORCHESTRATOR (Supervisor)               │  │
│  │                                                    │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │  │
│  │  │SPEND │ │ SLA  │ │RESRC │ │FINOPS│            │  │
│  │  │AGENT │ │AGENT │ │AGENT │ │AGENT │            │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  ENTERPRISE CONNECTORS                            │  │
│  │  SAP · Salesforce · AWS · JIRA · QuickBooks · CSV │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### 1. Clone the repo
```bash
git clone https://github.com/AhmedMoosani/costiq.git
cd costiq
```

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
cd ..
python -m uvicorn backend.api.main:app --reload --port 8000
```

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Open & Demo
1. Visit **http://localhost:3000** → Landing page
2. Click **"See It In Action"** → Dashboard
3. Click **"🚀 Run Analysis"** → Watch 4 agents find cost savings
4. Go to **Approvals** → Walk through the 3-step approval flow
5. Check **Impact Board** → See total savings with formulas

---

## 📁 Project Structure

```
costiq/
├── backend/
│   ├── api/main.py              # FastAPI app + WebSocket + REST
│   ├── agents/
│   │   ├── orchestrator.py      # Supervisor coordinating all agents
│   │   ├── spend_agent.py       # Duplicate invoices, rate creep
│   │   ├── sla_agent.py         # Breach prediction, intervention ROI
│   │   ├── resource_agent.py    # Cloud rightsizing, SaaS waste
│   │   ├── finops_agent.py      # Variance decomposition, reconciliation
│   │   └── base_agent.py        # Shared FIS logic + approval routing
│   ├── models/                  # Pydantic models (Finding, FIS, Approval)
│   ├── db/database.py           # In-memory DB (PostgreSQL in prod)
│   ├── scripts/generate_demo_data.py  # Synthetic data with anomalies
│   └── config.py                # Environment settings
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx             # Landing hero
│   │   └── dashboard/           # Dashboard, Findings, Approvals, Impact
│   ├── src/components/          # FindingCard, FISPanel, AgentFeed, Navbar
│   └── src/lib/api.ts           # API client + WebSocket
├── docker-compose.yml
└── README.md
```

---

## 🧮 The Math

### Spend Agent — Rate Creep Detection
```
savings = (invoiced_rate - contracted_rate) × volume × periods
        = ($55,860 - $42,000) × 18 invoices
        = $249,480
```

### SLA Agent — Expected Loss Prevention
```
P(breach) = 1 - exp(-λ × remaining_time)
E[loss] = P(breach) × penalty = 73% × $250,000 = $182,500
Intervention: Reroute 200 tickets ($800)
Net saving: $182,500 - $45,000 - $800 = $136,700
ROI: 170×
```

### Resource Agent — Cloud Rightsizing
```
waste = Σ(instance_cost × waste_factor)
     = 23 instances × avg $315/mo waste
     = $7,245/mo = $86,940/year
```

---

## 🎨 Design

- **Dark luxury theme** with dusty rose accent (#e4a4bd)
- **Glassmorphism** navigation and cards
- **Fluid orb** animated background
- **Animated stepper** for approval workflows
- **Real-time feed** via WebSocket
- **League Spartan** typography

---

## 📊 Evaluation Criteria

| Focus | How CostIQ Addresses It |
|-------|------------------------|
| **Show the math** | Every finding has a FIS with formula, baseline, projection, confidence |
| **Take action** | Agents execute vendor letters, ticket reroutes, PO amendments |
| **Data integration** | 6 connectors: SAP, Salesforce, AWS, JIRA, QuickBooks, CSV |
| **Approval workflows** | 4-tier routing with stepper UI and human-in-the-loop |

---

## 👥 Team

Built with ❤️ for the hackathon.

---

*Built for hackathon. Designed for production. Ship it.* 🚀
