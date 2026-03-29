"""
Demo Data Generator — Creates realistic enterprise data with embedded anomalies
for CostIQ agents to discover during the hackathon demo.

Intentionally plants:
- Rate creep on Acme Cloud Services ($249K overcharge)
- Duplicate invoices on TechVendor Pro ($18.5K)
- SLA breach risk at 73% probability ($182K exposure)
- 23 overprovisioned cloud instances ($87K waste)
- Budget variance of +15% on Marketing ($340K)
- Unreversed accruals ($45K)
"""
import random
from datetime import datetime, timedelta


def generate_demo_data() -> dict:
    """Generate complete demo dataset for all 4 agents."""
    return {
        # Spend Agent data
        "invoices": _generate_invoices(),
        "contracts": _generate_contracts(),
        
        # SLA Agent data
        "sla_configs": _generate_sla_configs(),
        "queue_metrics": _generate_queue_metrics(),
        "sla_contracts": _generate_sla_contracts(),
        
        # Resource Agent data
        "cloud_instances": _generate_cloud_instances(),
        "saas_apps": _generate_saas_apps(),
        "on_demand_monthly_spend": 28500,
        
        # FinOps Agent data
        "budget_vs_actual": _generate_budget_data(),
        "transactions": _generate_transactions(),
        "accruals": _generate_accruals(),
        
        # Metadata
        "data_sources": ["SAP_Demo", "AWS_CostExplorer", "JIRA", "QuickBooks", "CSV_Import"],
    }


def _generate_invoices() -> list:
    """Generate procurement invoices with embedded anomalies."""
    vendors = {
        "Acme Cloud Services": {"base": 42000, "category": "Cloud Infrastructure"},
        "TechVendor Pro": {"base": 18500, "category": "Software Services"},
        "GlobalSaaS Co.": {"base": 8200, "category": "SaaS Subscriptions"},
        "DataStream Inc.": {"base": 31000, "category": "Data Services"},
        "SecureNet Ltd.": {"base": 12000, "category": "Security Services"},
    }

    invoices = []

    # Normal invoices (200)
    for i in range(200):
        vendor = random.choice(list(vendors.keys()))
        config = vendors[vendor]
        invoices.append({
            "id": f"INV-{1000 + i}",
            "vendor": vendor,
            "amount": config["base"] * random.uniform(0.95, 1.05),
            "units": random.randint(800, 1200),
            "date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "line_item": "Monthly Services",
            "category": config["category"],
        })

    # ANOMALY 1: Rate creep — Acme invoices 33% over contract
    for i in range(18):
        invoices.append({
            "id": f"INV-RC-{i}",
            "vendor": "Acme Cloud Services",
            "amount": 55860,  # 42000 * 1.33
            "units": 1000,
            "date": (datetime.now() - timedelta(days=i * 30)).isoformat(),
            "line_item": "Monthly Services",
            "category": "Cloud Infrastructure",
        })

    # ANOMALY 2: Duplicate invoices
    invoices.append({
        "id": "INV-DUP-1",
        "vendor": "TechVendor Pro",
        "amount": 18500,
        "units": 1,
        "date": (datetime.now() - timedelta(days=28)).isoformat(),
        "line_item": "Monthly Services",
        "category": "Software Services",
    })
    invoices.append({
        "id": "INV-DUP-2",
        "vendor": "TechVendor Pro",
        "amount": 18500,
        "units": 1,
        "date": (datetime.now() - timedelta(days=26)).isoformat(),
        "line_item": "Monthly Services",
        "category": "Software Services",
    })

    return invoices


def _generate_contracts() -> dict:
    """Generate vendor contracts with contracted rates."""
    return {
        "Acme Cloud Services": {
            "contracted_rate": 42000,
            "contract_id": "MSA-2023-001",
            "effective_date": "2023-01-01",
            "expiry_date": "2026-12-31",
        },
        "TechVendor Pro": {
            "contracted_rate": 18500,
            "contract_id": "MSA-2023-002",
        },
        "GlobalSaaS Co.": {
            "contracted_rate": 8200,
            "contract_id": "MSA-2024-001",
        },
        "DataStream Inc.": {
            "contracted_rate": 31000,
            "contract_id": "MSA-2023-003",
        },
    }


def _generate_sla_configs() -> list:
    """Generate SLA service configurations."""
    return [
        {
            "service_id": "svc-001",
            "service_name": "Customer Support Tier 1",
            "target_hours": 4,
            "penalty_amount": 250000,
        },
        {
            "service_id": "svc-002",
            "service_name": "Infrastructure Monitoring",
            "target_hours": 2,
            "penalty_amount": 150000,
        },
        {
            "service_id": "svc-003",
            "service_name": "Order Processing",
            "target_hours": 8,
            "penalty_amount": 100000,
        },
    ]


def _generate_queue_metrics() -> list:
    """Generate queue metrics with breach risk signals."""
    return [
        {
            "service_id": "svc-001",
            "current_depth": 847,
            "baseline_depth": 450,
            "age_hours": 1.5,
            "avg_resolution_hours": 6.2,
            "avg_resolution_hours_30d": 6.2,
            "monthly_volume": 3200,
            "historical_breach_rate": 0.08,
        },
        {
            "service_id": "svc-002",
            "current_depth": 120,
            "baseline_depth": 100,
            "age_hours": 0.5,
            "avg_resolution_hours": 1.8,
            "avg_resolution_hours_30d": 1.8,
            "monthly_volume": 1500,
            "historical_breach_rate": 0.03,
        },
        {
            "service_id": "svc-003",
            "current_depth": 340,
            "baseline_depth": 300,
            "age_hours": 2,
            "avg_resolution_hours": 5.5,
            "avg_resolution_hours_30d": 5.5,
            "monthly_volume": 2800,
            "historical_breach_rate": 0.05,
        },
    ]


def _generate_sla_contracts() -> dict:
    """SLA penalty schedules."""
    return {
        "svc-001": {
            "penalty_amount": 250000,
            "penalty_per_breach": 500,
            "penalty_schedule": [
                {"tier": 1, "threshold": 0.95, "amount": 50000},
                {"tier": 2, "threshold": 0.90, "amount": 150000},
                {"tier": 3, "threshold": 0.85, "amount": 250000},
            ],
        },
        "svc-002": {
            "penalty_amount": 150000,
            "penalty_per_breach": 300,
            "penalty_schedule": [
                {"tier": 1, "threshold": 0.95, "amount": 30000},
                {"tier": 2, "threshold": 0.90, "amount": 100000},
                {"tier": 3, "threshold": 0.85, "amount": 150000},
            ],
        },
    }


def _generate_cloud_instances() -> list:
    """Generate cloud instance data with overprovisioned instances."""
    instances = []
    
    # Well-utilized instances
    for i in range(30):
        instances.append({
            "instance_id": f"i-{random.randint(10000, 99999)}",
            "instance_type": random.choice(["m5.xlarge", "c5.2xlarge", "r5.large"]),
            "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
            "avg_cpu_pct": random.uniform(45, 85),
            "monthly_cost": random.uniform(200, 800),
            "recommended_type": None,
        })

    # ANOMALY: Overprovisioned instances (23 with <30% CPU)
    for i in range(23):
        inst_type = random.choice(["m5.4xlarge", "c5.4xlarge", "r5.2xlarge", "m5.8xlarge"])
        cost = {"m5.4xlarge": 560, "c5.4xlarge": 490, "r5.2xlarge": 380, "m5.8xlarge": 1120}[inst_type]
        smaller = {"m5.4xlarge": "m5.xlarge", "c5.4xlarge": "c5.xlarge", "r5.2xlarge": "r5.large", "m5.8xlarge": "m5.2xlarge"}[inst_type]
        
        instances.append({
            "instance_id": f"i-waste-{i:03d}",
            "instance_type": inst_type,
            "region": random.choice(["us-east-1", "us-west-2"]),
            "avg_cpu_pct": random.uniform(5, 25),
            "monthly_cost": cost,
            "recommended_type": smaller,
        })

    return instances


def _generate_saas_apps() -> list:
    """Generate SaaS subscription data with underutilized licenses."""
    return [
        {
            "name": "Salesforce Enterprise",
            "total_seats": 500,
            "active_users_30d": 312,
            "per_seat_monthly": 150,
        },
        {
            "name": "Slack Business+",
            "total_seats": 1200,
            "active_users_30d": 890,
            "per_seat_monthly": 12.50,
        },
        {
            "name": "Zoom Enterprise",
            "total_seats": 800,
            "active_users_30d": 340,  # Very underutilized!
            "per_seat_monthly": 20,
        },
        {
            "name": "Jira Cloud Premium",
            "total_seats": 300,
            "active_users_30d": 275,
            "per_seat_monthly": 14,
        },
        {
            "name": "Adobe Creative Cloud",
            "total_seats": 150,
            "active_users_30d": 45,   # Severely underutilized
            "per_seat_monthly": 55,
        },
    ]


def _generate_budget_data() -> list:
    """Generate budget vs actual with significant variances."""
    return [
        {
            "cost_center": "Marketing",
            "account": "MKT-001",
            "budget_total": 2200000,
            "actual_total": 2540000,
            "budget_units": 44000,
            "actual_units": 48000,
            "budget_rate": 50.0,
            "actual_rate": 52.92,
            "root_cause": "VOLUME — increased ad spend for Q4 campaign without budget amendment",
        },
        {
            "cost_center": "Engineering",
            "account": "ENG-001",
            "budget_total": 4500000,
            "actual_total": 4200000,
            "budget_units": 90000,
            "actual_units": 84000,
            "budget_rate": 50.0,
            "actual_rate": 50.0,
        },
        {
            "cost_center": "Cloud Operations",
            "account": "OPS-001",
            "budget_total": 1800000,
            "actual_total": 2160000,  # 20% over
            "budget_units": 30000,
            "actual_units": 32000,
            "budget_rate": 60.0,
            "actual_rate": 67.5,
            "root_cause": "RATE — cloud pricing tier exceeded, triggering premium rates",
        },
    ]


def _generate_transactions() -> list:
    """Generate transactions with reconciliation discrepancies."""
    transactions = []
    
    # Matching transactions
    for i in range(50):
        amount = random.uniform(5000, 50000)
        ref = f"TXN-{2000 + i}"
        transactions.append({"id": f"{ref}-GL", "reference": ref, "amount": amount, "system": "General Ledger"})
        transactions.append({"id": f"{ref}-BK", "reference": ref, "amount": amount, "system": "Bank Statement"})

    # ANOMALY: Mismatched transactions
    for i in range(8):
        ref = f"TXN-DISC-{i}"
        base = random.uniform(10000, 80000)
        disc = random.uniform(500, 5000)
        transactions.append({"id": f"{ref}-GL", "reference": ref, "amount": base, "system": "General Ledger"})
        transactions.append({"id": f"{ref}-BK", "reference": ref, "amount": base + disc, "system": "Bank Statement"})

    return transactions


def _generate_accruals() -> list:
    """Generate accruals with some unreversed entries."""
    accruals = []
    
    # Normal (reversed)
    for i in range(20):
        accruals.append({
            "id": f"ACC-{100 + i}",
            "amount": random.uniform(2000, 15000),
            "age_days": random.randint(5, 25),
            "reversed": True,
            "description": f"Monthly accrual - period {i}",
        })

    # ANOMALY: Unreversed accruals (stale)
    for i in range(6):
        accruals.append({
            "id": f"ACC-STALE-{i}",
            "amount": random.uniform(5000, 12000),
            "age_days": random.randint(35, 90),
            "reversed": False,
            "description": f"Q3 accrual - vendor payment pending",
        })

    return accruals
