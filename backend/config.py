"""
CostIQ Configuration — Environment variables and settings.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR}/costiq.db")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", f"sqlite:///{DATA_DIR}/costiq.db")

# Redis (optional — falls back to in-memory)
REDIS_URL = os.getenv("REDIS_URL", "")

# LLM
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")

# Mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# Approval thresholds
APPROVAL_TIERS = {
    "auto_execute":  {"threshold": 5_000, "approvers": []},
    "manager":       {"threshold": 50_000, "approvers": ["dept_manager"]},
    "director":      {"threshold": 250_000, "approvers": ["director", "finance"]},
    "c_suite":       {"threshold": 1_000_000, "approvers": ["cfo", "ceo"]},
}
