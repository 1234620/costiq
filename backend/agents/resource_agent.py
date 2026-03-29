"""
Resource Optimization Agent — Monitors utilization across cloud, SaaS, and teams.
Recommends consolidation, rightsizing, and reserved instance purchases.

Key Formulas:
- Cloud: savings = current_cost - optimal_cost (based on utilization)
- SaaS: inactive_cost = inactive_seats × per_seat_cost × (1 - buffer)
- RI: savings = on_demand - reserved (35-55% discount)
"""
from typing import List, Dict
from backend.agents.base_agent import BaseAgent
from backend.models.finding import Finding


class ResourceAgent(BaseAgent):
    AGENT_TYPE = "resource"
    AGENT_NAME = "Resource Optimization Agent"
    AGENT_COLOR = "#60a5fa"

    async def analyze(self, data: dict) -> List[Finding]:
        """Analyze cloud, SaaS, and human resource utilization."""
        findings = []
        run_id = data.get("run_id", "")

        # Cloud infrastructure
        cloud_instances = data.get("cloud_instances", [])
        if cloud_instances:
            findings.extend(self._analyze_cloud(cloud_instances, run_id))

        # SaaS licenses
        saas_apps = data.get("saas_apps", [])
        if saas_apps:
            findings.extend(self._analyze_saas(saas_apps, run_id))

        # Reserved instance opportunities
        on_demand_spend = data.get("on_demand_monthly_spend", 0)
        if on_demand_spend > 0:
            findings.extend(self._analyze_reserved_instances(on_demand_spend, run_id))

        return findings

    def _analyze_cloud(self, instances: List[dict], run_id: str) -> List[Finding]:
        """Analyze cloud instance utilization for rightsizing."""
        findings = []
        overprovisioned = []
        total_waste = 0

        for inst in instances:
            cpu_pct = inst.get("avg_cpu_pct", 50)
            monthly_cost = inst.get("monthly_cost", 0)
            
            if cpu_pct < 30:  # Under 30% utilization = overprovisioned
                # Estimate optimal size saves ~40-60% based on utilization
                waste_factor = 1 - (cpu_pct / 100) * 2  # Scale savings by how idle
                waste_factor = min(0.6, max(0.2, waste_factor))
                monthly_waste = monthly_cost * waste_factor
                total_waste += monthly_waste
                
                overprovisioned.append({
                    **inst,
                    "waste_factor": waste_factor,
                    "monthly_waste": monthly_waste,
                })

        if overprovisioned:
            annual_waste = total_waste * 12
            
            # Create individual findings for high-cost instances
            top_instances = sorted(overprovisioned, key=lambda x: x["monthly_waste"], reverse=True)
            
            # Summary finding
            findings.append(self.create_finding(
                finding_type="cloud_rightsizing",
                title=f"{len(overprovisioned)} Cloud Instances Overprovisioned",
                description=(
                    f"Found {len(overprovisioned)} instances with <30% average CPU utilization. "
                    f"Total monthly waste: ${total_waste:,.0f}. "
                    f"Top offender: {top_instances[0].get('instance_id', 'N/A')} "
                    f"({top_instances[0].get('instance_type', 'N/A')}) at "
                    f"{top_instances[0].get('avg_cpu_pct', 0):.0f}% CPU, "
                    f"wasting ${top_instances[0].get('monthly_waste', 0):,.0f}/mo."
                ),
                severity="high" if annual_waste > 50000 else "medium",
                baseline_cost=sum(i.get("monthly_cost", 0) for i in overprovisioned) * 12,
                projected_savings=annual_waste,
                annualized_savings=annual_waste,
                confidence_score=0.88,
                formula=(
                    f"waste = Σ(instance_cost × waste_factor) = ${total_waste:,.0f}/mo = "
                    f"${annual_waste:,.0f}/year\n"
                    f"waste_factor = 1 - (utilization% / 100) × 2, capped [0.2, 0.6]"
                ),
                action_description=(
                    f"Downsize {len(overprovisioned)} instances to right-sized alternatives. "
                    f"Start with {top_instances[0].get('instance_id', 'N/A')} → "
                    f"{top_instances[0].get('recommended_type', 'smaller instance')}."
                ),
                data_sources=[f"instance_{i.get('instance_id', 'N/A')}" for i in top_instances[:5]],
                run_id=run_id,
            ))

        return findings

    def _analyze_saas(self, apps: List[dict], run_id: str) -> List[Finding]:
        """Analyze SaaS license utilization."""
        findings = []

        for app in apps:
            total_seats = app.get("total_seats", 0)
            active_users = app.get("active_users_30d", 0)
            per_seat_cost = app.get("per_seat_monthly", 0)
            app_name = app.get("name", "Unknown App")

            if total_seats == 0 or per_seat_cost == 0:
                continue

            inactive_seats = total_seats - active_users
            utilization = active_users / total_seats

            if utilization < 0.75:  # Less than 75% utilized
                buffer_factor = 0.15  # Keep 15% buffer for growth
                reclaimable = max(0, inactive_seats - int(total_seats * buffer_factor))
                monthly_savings = reclaimable * per_seat_cost
                annual_savings = monthly_savings * 12

                if annual_savings > 1000:
                    findings.append(self.create_finding(
                        finding_type="saas_license_waste",
                        title=f"Unused {app_name} Licenses — {reclaimable} Seats Reclaimable",
                        description=(
                            f"{app_name}: {active_users}/{total_seats} seats active in last 30 days "
                            f"({utilization:.0%} utilization). {inactive_seats} inactive seats, "
                            f"{reclaimable} reclaimable after 15% growth buffer."
                        ),
                        severity="medium" if annual_savings < 20000 else "high",
                        baseline_cost=total_seats * per_seat_cost * 12,
                        projected_savings=annual_savings,
                        annualized_savings=annual_savings,
                        confidence_score=0.91,
                        formula=(
                            f"inactive = {total_seats} - {active_users} = {inactive_seats} seats\n"
                            f"reclaimable = {inactive_seats} - buffer({int(total_seats * buffer_factor)}) = {reclaimable}\n"
                            f"savings = {reclaimable} × ${per_seat_cost}/seat/mo × 12 = ${annual_savings:,.0f}/yr"
                        ),
                        action_description=f"Revoke {reclaimable} inactive {app_name} licenses and reduce subscription tier",
                        data_sources=[f"saas_{app_name.replace(' ', '_')}_usage_report"],
                        run_id=run_id,
                    ))

        return findings

    def _analyze_reserved_instances(self, on_demand_monthly: float, run_id: str) -> List[Finding]:
        """Calculate Reserved Instance vs On-Demand savings."""
        findings = []

        # 1-year RI: ~35% discount
        ri_1yr_monthly = on_demand_monthly * 0.65
        savings_1yr = (on_demand_monthly - ri_1yr_monthly) * 12

        # 3-year RI: ~55% discount
        ri_3yr_monthly = on_demand_monthly * 0.45
        savings_3yr = (on_demand_monthly - ri_3yr_monthly) * 12

        if savings_1yr > 5000:
            findings.append(self.create_finding(
                finding_type="reserved_instance_opportunity",
                title=f"Reserved Instance Savings — ${savings_1yr:,.0f}/year (1-Year Commitment)",
                description=(
                    f"Current on-demand spend: ${on_demand_monthly:,.0f}/month. "
                    f"1-year Reserved Instance commitment saves 35% (${savings_1yr:,.0f}/year). "
                    f"3-year commitment saves 55% (${savings_3yr:,.0f}/year)."
                ),
                severity="high" if savings_1yr > 50000 else "medium",
                baseline_cost=on_demand_monthly * 12,
                projected_savings=savings_1yr,
                annualized_savings=savings_1yr,
                confidence_score=0.94,
                formula=(
                    f"1yr RI savings = ${on_demand_monthly:,.0f}/mo × 35% × 12 = ${savings_1yr:,.0f}/yr\n"
                    f"3yr RI savings = ${on_demand_monthly:,.0f}/mo × 55% × 12 = ${savings_3yr:,.0f}/yr"
                ),
                action_description=(
                    f"Purchase 1-year Reserved Instances for stable baseline workloads. "
                    f"Consider 3-year for guaranteed baseline (saves additional ${savings_3yr - savings_1yr:,.0f}/yr)."
                ),
                data_sources=["aws_cost_explorer", "compute_optimizer"],
                run_id=run_id,
            ))

        return findings
