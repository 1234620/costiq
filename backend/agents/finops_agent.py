"""
Financial Operations Agent — Reconciliation, variance analysis, close cycle acceleration.

Key Math:
- Variance decomposition: Δ = Volume_Δ + Rate_Δ + Mix_Δ
- Volume: (actual_units - budget_units) × budget_rate
- Rate: (actual_rate - budget_rate) × budget_units
- Mix: total_variance - volume - rate (interaction effect)
"""
from typing import List, Dict
from backend.agents.base_agent import BaseAgent
from backend.models.finding import Finding


class FinOpsAgent(BaseAgent):
    AGENT_TYPE = "finops"
    AGENT_NAME = "Financial Operations Agent"
    AGENT_COLOR = "#10b981"

    async def analyze(self, data: dict) -> List[Finding]:
        """Analyze financial data for reconciliation issues and variances."""
        findings = []
        run_id = data.get("run_id", "")

        # Budget vs Actual variance analysis
        budget_data = data.get("budget_vs_actual", [])
        if budget_data:
            findings.extend(self._analyze_variances(budget_data, run_id))

        # Transaction reconciliation
        transactions = data.get("transactions", [])
        if transactions:
            findings.extend(self._reconcile_transactions(transactions, run_id))

        # Accrual analysis
        accruals = data.get("accruals", [])
        if accruals:
            findings.extend(self._analyze_accruals(accruals, run_id))

        return findings

    def _analyze_variances(self, budget_data: List[dict], run_id: str) -> List[Finding]:
        """Decompose budget vs actual variances into volume, rate, and mix effects."""
        findings = []

        for item in budget_data:
            actual_total = item.get("actual_total", 0)
            budget_total = item.get("budget_total", 0)
            
            if budget_total == 0:
                continue

            total_variance = actual_total - budget_total
            variance_pct = (total_variance / budget_total) * 100
            
            # Only flag significant variances (>5%)
            if abs(variance_pct) < 5:
                continue

            # Decompose variance
            actual_units = item.get("actual_units", actual_total)
            budget_units = item.get("budget_units", budget_total)
            actual_rate = item.get("actual_rate", 1)
            budget_rate = item.get("budget_rate", 1)

            volume_variance = (actual_units - budget_units) * budget_rate
            rate_variance = (actual_rate - budget_rate) * budget_units
            mix_variance = total_variance - volume_variance - rate_variance

            # Determine largest driver
            components = [
                ("volume", volume_variance),
                ("rate", rate_variance),
                ("mix", mix_variance),
            ]
            largest_driver = max(components, key=lambda x: abs(x[1]))

            # Classify root cause
            root_cause = self._classify_root_cause(item, largest_driver[0])
            
            cost_center = item.get("cost_center", item.get("account", "Unknown"))
            correctable_amount = abs(total_variance) * 0.7  # Estimate 70% correctable

            severity = "critical" if abs(variance_pct) > 20 else "high" if abs(variance_pct) > 10 else "medium"

            findings.append(self.create_finding(
                finding_type="budget_variance",
                title=f"Budget Variance {variance_pct:+.1f}% — {cost_center}",
                description=(
                    f"{cost_center}: Actual ${actual_total:,.0f} vs Budget ${budget_total:,.0f} "
                    f"({variance_pct:+.1f}%). Largest driver: {largest_driver[0]} effect "
                    f"(${largest_driver[1]:+,.0f}). Root cause: {root_cause}."
                ),
                severity=severity,
                baseline_cost=abs(total_variance),
                projected_savings=correctable_amount,
                annualized_savings=correctable_amount * 4,  # Quarterly × 4
                confidence_score=0.82,
                formula=(
                    f"Total Δ = ${total_variance:+,.0f} ({variance_pct:+.1f}%)\n"
                    f"  Volume Δ = ({actual_units:,.0f} - {budget_units:,.0f}) × ${budget_rate:,.2f} = ${volume_variance:+,.0f}\n"
                    f"  Rate Δ = (${actual_rate:,.2f} - ${budget_rate:,.2f}) × {budget_units:,.0f} = ${rate_variance:+,.0f}\n"
                    f"  Mix Δ = ${mix_variance:+,.0f}\n"
                    f"  Δ = Volume + Rate + Mix"
                ),
                action_description=(
                    f"Investigate {largest_driver[0]} variance in {cost_center}. "
                    f"Root cause: {root_cause}. Estimated correctable: ${correctable_amount:,.0f}."
                ),
                data_sources=[
                    f"budget_{cost_center.replace(' ', '_')}",
                    f"actuals_{cost_center.replace(' ', '_')}",
                    "gl_transactions",
                ],
                run_id=run_id,
            ))

        return findings

    def _reconcile_transactions(self, transactions: List[dict], run_id: str) -> List[Finding]:
        """Find reconciliation discrepancies between systems."""
        findings = []
        
        # Group by reference number to find mismatches
        by_ref = {}
        for txn in transactions:
            ref = txn.get("reference", txn.get("id", ""))
            if ref not in by_ref:
                by_ref[ref] = []
            by_ref[ref].append(txn)

        discrepancies = []
        total_discrepancy = 0

        for ref, txns in by_ref.items():
            if len(txns) < 2:
                continue

            amounts = [t.get("amount", 0) for t in txns]
            if len(set(amounts)) > 1:  # Mismatch found
                disc = max(amounts) - min(amounts)
                total_discrepancy += disc
                discrepancies.append({
                    "reference": ref,
                    "amounts": amounts,
                    "systems": [t.get("system", "unknown") for t in txns],
                    "discrepancy": disc,
                })

        if discrepancies:
            findings.append(self.create_finding(
                finding_type="reconciliation_discrepancy",
                title=f"{len(discrepancies)} Reconciliation Discrepancies Found",
                description=(
                    f"Cross-system reconciliation found {len(discrepancies)} transactions "
                    f"with amount mismatches. Total discrepancy: ${total_discrepancy:,.0f}. "
                    f"Systems involved: {', '.join(set(d['systems'][0] for d in discrepancies[:3]))}."
                ),
                severity="high" if total_discrepancy > 50000 else "medium",
                baseline_cost=total_discrepancy,
                projected_savings=total_discrepancy * 0.85,
                annualized_savings=total_discrepancy * 0.85 * 4,
                confidence_score=0.90,
                formula=(
                    f"discrepancy = Σ|system_A_amount - system_B_amount| = ${total_discrepancy:,.0f}\n"
                    f"correctable (est. 85%) = ${total_discrepancy * 0.85:,.0f}"
                ),
                action_description=(
                    f"Create journal entry drafts for {len(discrepancies)} discrepancies. "
                    f"Flag top {min(5, len(discrepancies))} for controller review."
                ),
                data_sources=["gl_transactions", "bank_statements", "erp_ledger"],
                run_id=run_id,
            ))

        return findings

    def _analyze_accruals(self, accruals: List[dict], run_id: str) -> List[Finding]:
        """Check for unreversed accruals and timing issues."""
        findings = []
        unreversed = [a for a in accruals if not a.get("reversed", False) and a.get("age_days", 0) > 30]
        
        if unreversed:
            total = sum(a.get("amount", 0) for a in unreversed)
            if total > 5000:
                findings.append(self.create_finding(
                    finding_type="unreversed_accruals",
                    title=f"{len(unreversed)} Unreversed Accruals — ${total:,.0f}",
                    description=(
                        f"Found {len(unreversed)} accruals older than 30 days that haven't been reversed. "
                        f"Total balance: ${total:,.0f}. These may be inflating period expenses."
                    ),
                    severity="medium",
                    baseline_cost=total,
                    projected_savings=total * 0.6,
                    annualized_savings=total * 0.6,
                    confidence_score=0.78,
                    formula=f"unreversed_balance = Σ(accrual_amounts) = ${total:,.0f}; est. 60% correctable",
                    action_description=f"Review and reverse {len(unreversed)} stale accruals totaling ${total:,.0f}",
                    data_sources=["accrual_ledger", "gl_transactions"],
                    run_id=run_id,
                ))

        return findings

    @staticmethod
    def _classify_root_cause(item: dict, driver: str) -> str:
        """Classify root cause from taxonomy."""
        cause = item.get("root_cause", "")
        if cause:
            return cause
        
        mapping = {
            "volume": "VOLUME — more/fewer transactions than planned",
            "rate": "RATE — price/rate changed vs assumption",
            "mix": "MIX — product/service mix shifted",
        }
        return mapping.get(driver, "UNKNOWN — requires investigation")
