"""
SLA & Penalty Prevention Agent — Predicts SLA breaches BEFORE they happen,
calculates expected financial loss, and recommends interventions with ROI.

Key Math:
- P(breach) = 1 - P(resolve within SLA)
- P(resolve) = 1 - exp(-λ × remaining_time), λ = 1/avg_resolution
- Expected loss = P(breach) × penalty_amount
- Intervention ROI = (loss_prevented - intervention_cost) / intervention_cost
"""
import math
from typing import List, Dict
from backend.agents.base_agent import BaseAgent
from backend.models.finding import Finding


class SLAAgent(BaseAgent):
    AGENT_TYPE = "sla"
    AGENT_NAME = "SLA & Penalty Prevention Agent"
    AGENT_COLOR = "#f59e0b"

    async def analyze(self, data: dict) -> List[Finding]:
        """Analyze SLA data for breach risks and prevention opportunities."""
        findings = []
        sla_configs = data.get("sla_configs", [])
        queue_metrics = data.get("queue_metrics", [])
        contracts = data.get("contracts", {})
        run_id = data.get("run_id", "")

        if not sla_configs or not queue_metrics:
            return findings

        for config in sla_configs:
            service_id = config.get("service_id", "")
            metrics = next(
                (m for m in queue_metrics if m.get("service_id") == service_id),
                None
            )
            if not metrics:
                continue

            contract = contracts.get(service_id, {})
            
            # Calculate breach probability
            p_breach = self._calculate_breach_probability(metrics, config)
            
            if p_breach > 0.30:  # Only flag if >30% breach risk
                # Calculate expected financial loss
                penalty_amount = contract.get("penalty_amount", config.get("penalty_amount", 50000))
                expected_loss = p_breach * penalty_amount
                
                # Calculate intervention options
                intervention = self._calculate_intervention(metrics, config, p_breach, penalty_amount)
                
                severity = "critical" if p_breach > 0.70 else "high" if p_breach > 0.50 else "medium"
                
                findings.append(self.create_finding(
                    finding_type="sla_breach_risk",
                    title=f"SLA Breach Risk — {config.get('service_name', service_id)} ({p_breach:.0%} probability)",
                    description=(
                        f"Service {config.get('service_name', service_id)} has a {p_breach:.0%} probability of "
                        f"SLA breach within the next {config.get('target_hours', 4)} hours. "
                        f"Current queue: {metrics.get('current_depth', 0)} tickets, "
                        f"avg resolution: {metrics.get('avg_resolution_hours', 0):.1f} hours, "
                        f"SLA target: {config.get('target_hours', 4)} hours. "
                        f"Maximum penalty exposure: ${penalty_amount:,.0f}."
                    ),
                    severity=severity,
                    baseline_cost=expected_loss,
                    projected_savings=intervention["net_saving"],
                    annualized_savings=intervention["net_saving"] * 12,
                    confidence_score=min(0.95, 0.6 + p_breach * 0.3),
                    formula=(
                        f"E[loss] = P(breach) × penalty = {p_breach:.2%} × ${penalty_amount:,.0f} = ${expected_loss:,.0f}\n"
                        f"Intervention cost: ${intervention['cost']:,.0f}\n"
                        f"Post-intervention E[loss]: ${intervention['post_expected_loss']:,.0f}\n"
                        f"Net saving: ${intervention['net_saving']:,.0f}\n"
                        f"ROI: {intervention['roi']}"
                    ),
                    intervention_cost=intervention["cost"],
                    action_description=intervention["action"],
                    data_sources=[
                        f"queue_metrics_{service_id}",
                        f"sla_config_{service_id}",
                        f"contract_{service_id}",
                    ],
                    payback_period="immediate",
                    run_id=run_id,
                ))

            # Also check for historical breach patterns
            historical_findings = self._analyze_historical_breaches(config, metrics, contract, run_id)
            findings.extend(historical_findings)

        return findings

    def _calculate_breach_probability(self, metrics: dict, sla_config: dict) -> float:
        """
        Bayesian estimate of SLA breach probability.
        Uses exponential distribution with queue-depth multiplier.
        """
        target_hours = sla_config.get("target_hours", 4)
        age_hours = metrics.get("age_hours", 0)
        remaining_hours = max(0.1, target_hours - age_hours)
        avg_resolution = metrics.get("avg_resolution_hours", 3.0)
        current_depth = metrics.get("current_depth", 100)
        baseline_depth = metrics.get("baseline_depth", 100)
        
        # Queue depth multiplier
        queue_multiplier = max(1.0, current_depth / max(baseline_depth, 1))
        adjusted_avg = avg_resolution * min(queue_multiplier, 3.0)  # Cap at 3x
        
        # Exponential distribution CDF
        lambda_rate = 1 / max(adjusted_avg, 0.1)
        p_resolve = 1 - math.exp(-lambda_rate * remaining_hours)
        p_breach = 1 - p_resolve
        
        return min(0.99, max(0.01, p_breach))

    def _calculate_intervention(self, metrics: dict, config: dict, 
                                 p_breach: float, penalty: float) -> dict:
        """Calculate intervention cost, post-intervention risk, and ROI."""
        current_depth = metrics.get("current_depth", 100)
        baseline_depth = metrics.get("baseline_depth", 100)
        
        # Intervention: reroute tickets to reduce queue
        tickets_to_reroute = max(0, current_depth - int(baseline_depth * 0.9))
        reroute_cost = tickets_to_reroute * 4  # $4 per ticket reroute cost
        
        # Post-intervention breach probability
        new_depth = current_depth - tickets_to_reroute
        new_metrics = {**metrics, "current_depth": new_depth}
        p_breach_after = self._calculate_breach_probability(new_metrics, config)
        
        post_expected_loss = p_breach_after * penalty
        pre_expected_loss = p_breach * penalty
        net_saving = pre_expected_loss - post_expected_loss - reroute_cost
        
        roi_pct = ((net_saving) / max(reroute_cost, 1)) * 100
        
        return {
            "action": (
                f"Reroute {tickets_to_reroute} tickets to overflow team "
                f"(cost: ${reroute_cost:,.0f}). Reduces P(breach) from "
                f"{p_breach:.0%} to {p_breach_after:.0%}."
            ),
            "cost": reroute_cost,
            "tickets_rerouted": tickets_to_reroute,
            "p_breach_after": p_breach_after,
            "post_expected_loss": post_expected_loss,
            "net_saving": max(0, net_saving),
            "roi": f"{roi_pct:.0f}×" if roi_pct > 100 else f"{roi_pct:.0f}%",
        }

    def _analyze_historical_breaches(self, config: dict, metrics: dict, 
                                      contract: dict, run_id: str) -> List[Finding]:
        """Analyze historical breach rate for proactive prevention."""
        findings = []
        historical_breach_rate = metrics.get("historical_breach_rate", 0)
        monthly_ticket_volume = metrics.get("monthly_volume", 0)
        penalty_per_breach = contract.get("penalty_per_breach", 0)
        
        if historical_breach_rate > 0.05 and penalty_per_breach > 0:
            monthly_penalty_exposure = monthly_ticket_volume * historical_breach_rate * penalty_per_breach
            annual_exposure = monthly_penalty_exposure * 12
            
            if annual_exposure > 10000:
                findings.append(self.create_finding(
                    finding_type="chronic_sla_risk",
                    title=f"Chronic SLA Breach Pattern — {config.get('service_name', '')}",
                    description=(
                        f"Historical breach rate of {historical_breach_rate:.1%} on "
                        f"{monthly_ticket_volume} monthly tickets creates annualized penalty "
                        f"exposure of ${annual_exposure:,.0f}."
                    ),
                    severity="high",
                    baseline_cost=annual_exposure,
                    projected_savings=annual_exposure * 0.6,
                    annualized_savings=annual_exposure * 0.6,
                    confidence_score=0.85,
                    formula=(
                        f"annual_exposure = {monthly_ticket_volume} tickets/mo × "
                        f"{historical_breach_rate:.1%} breach_rate × "
                        f"${penalty_per_breach:,.0f}/breach × 12 = ${annual_exposure:,.0f}"
                    ),
                    action_description="Implement capacity planning adjustments and automated queue balancing",
                    data_sources=[f"historical_metrics_{config.get('service_id', '')}"],
                    run_id=run_id,
                ))

        return findings
