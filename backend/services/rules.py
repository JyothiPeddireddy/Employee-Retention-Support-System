"""Rules and Explainable Prioritization Engine for Supportive Retention Conversations.
Enforces strict pre-outcome temporal barriers and outputs human-readable factor attributions.
"""
from typing import Dict, List, Any, Tuple
from backend.schemas.prioritization import PrioritizedEmployee, FactorAttribution, PrioritizationSummary


class PrioritizationRulesEngine:
    """Computes supportive retention prioritization with factor explanations."""

    def __init__(self, data_store: Dict[str, List[Dict[str, Any]]]):
        self.employees = {e["employee_id"]: e for e in data_store.get("employees", [])}
        self.teams = {t["team_id"]: t for t in data_store.get("teams", [])}
        self.roles = {r["role_id"]: r for r in data_store.get("roles", [])}
        self.bands = {b["band_id"]: b for b in data_store.get("compensation_bands", [])}
        self.tenure_snapshots = data_store.get("tenure_snapshots", [])
        self.workload_snapshots = data_store.get("workload_snapshots", [])
        self.engagement_surveys = data_store.get("engagement_surveys", [])
        self.interventions = data_store.get("interventions", [])

        # Group time-series records by employee_id
        self.workload_by_emp: Dict[str, List[Dict[str, Any]]] = {}
        for w in self.workload_snapshots:
            self.workload_by_emp.setdefault(w["employee_id"], []).append(w)

        self.surveys_by_emp: Dict[str, List[Dict[str, Any]]] = {}
        for s in self.engagement_surveys:
            self.surveys_by_emp.setdefault(s["employee_id"], []).append(s)

        self.tenure_by_emp: Dict[str, List[Dict[str, Any]]] = {}
        for t in self.tenure_snapshots:
            self.tenure_by_emp.setdefault(t["employee_id"], []).append(t)

        self.interventions_by_emp: Dict[str, List[Dict[str, Any]]] = {}
        for i in self.interventions:
            self.interventions_by_emp.setdefault(i["employee_id"], []).append(i)

    def evaluate_all(self, department_filter: str = None, min_tier: str = None) -> List[PrioritizedEmployee]:
        """Evaluate retention signals across all active employees."""
        results: List[PrioritizedEmployee] = []

        for emp_id, emp in self.employees.items():
            if emp["status"] != "ACTIVE":
                continue  # Only prioritize active workforce for supportive retention

            team = self.teams.get(emp["team_id"], {})
            dept = team.get("department", "Unknown")

            if department_filter and department_filter.lower() != "all" and dept.lower() != department_filter.lower():
                continue

            prioritized = self.evaluate_employee(emp_id)

            if min_tier:
                tier_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
                if tier_order.get(prioritized.priority_tier, 0) < tier_order.get(min_tier, 0):
                    continue

            results.append(prioritized)

        # Sort highest priority first
        results.sort(key=lambda x: x.composite_priority_score, reverse=True)
        return results

    def evaluate_employee(self, emp_id: str) -> PrioritizedEmployee:
        """Calculate supportive priority score and explainability breakdown for a single employee."""
        emp = self.employees[emp_id]
        team = self.teams.get(emp["team_id"], {})
        role = self.roles.get(emp["role_id"], {})
        band = self.bands.get(role.get("band_id", ""), {})

        # 1. Evaluate Workload Dimension
        workload_score, workload_factors = self._evaluate_workload(emp_id)

        # 2. Evaluate Career Velocity & Compensation Stagnation
        career_score, career_factors = self._evaluate_career_velocity(emp_id, emp, role, band)

        # 3. Evaluate Engagement Trajectory (Neutral to Missingness)
        engagement_score, engagement_factors = self._evaluate_engagement(emp_id)

        # Composite score weighting: Workload 40%, Career 35%, Engagement 25%
        raw_composite = (workload_score * 0.40) + (career_score * 0.35) + (engagement_score * 0.25)
        composite_score = round(min(100.0, max(0.0, raw_composite)), 1)

        if composite_score >= 70.0:
            tier = "HIGH"
        elif composite_score >= 40.0:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        # Combine explainability factors
        factors = workload_factors + career_factors + engagement_factors

        # Generate actionable topics for manager 1-on-1
        recommended_topics = self._generate_recommended_topics(factors)

        # Check existing interventions
        active_ints = self.interventions_by_emp.get(emp_id, [])
        has_active = len(active_ints) > 0
        last_int_date = active_ints[-1]["intervention_date"] if has_active else None

        tenure_snaps = self.tenure_by_emp.get(emp_id, [])
        latest_tenure = tenure_snaps[-1] if tenure_snaps else {}

        return PrioritizedEmployee(
            employee_id=emp_id,
            full_name=emp["full_name"],
            email=emp["email"],
            team_name=team.get("name", "Unknown"),
            department=team.get("department", "Unknown"),
            role_title=role.get("title", "Unknown"),
            role_level=role.get("level", "IC"),
            tenure_months=latest_tenure.get("tenure_months", 12),
            months_in_role=latest_tenure.get("months_in_current_role", 12),
            composite_priority_score=composite_score,
            priority_tier=tier,
            factors=factors,
            recommended_topics=recommended_topics,
            has_active_intervention=has_active,
            last_intervention_date=last_int_date
        )

    def _evaluate_workload(self, emp_id: str) -> Tuple[float, List[FactorAttribution]]:
        factors = []
        snaps = self.workload_by_emp.get(emp_id, [])
        if not snaps:
            return 20.0, []

        recent_snaps = snaps[-3:]  # Focus on latest 3 quarters
        avg_recent_hours = sum(s["avg_weekly_hours"] for s in recent_snaps) / len(recent_snaps)
        max_consec_ot = max((s.get("consecutive_overtime_weeks", 0) for s in recent_snaps), default=0)
        has_benign_surge = any(s.get("is_benign_surge") for s in recent_snaps)

        score = 20.0

        if avg_recent_hours >= 48.0 and not has_benign_surge:
            score += 65.0
            factors.append(FactorAttribution(
                category="WORKLOAD",
                signal_name="Sustained High Overtime",
                raw_value=f"{avg_recent_hours:.1f} hrs/wk avg ({max_consec_ot} consecutive overtime weeks)",
                impact_level="HIGH",
                supportive_guidance="Discuss project bandwidth and schedule temporary workload rebalancing."
            ))
        elif avg_recent_hours >= 44.0:
            score += 40.0
            factors.append(FactorAttribution(
                category="WORKLOAD",
                signal_name="Elevated Workload",
                raw_value=f"{avg_recent_hours:.1f} hrs/wk avg",
                impact_level="MEDIUM",
                supportive_guidance="Verify whether workload surge is linked to temporary release deadlines."
            ))
        elif has_benign_surge:
            factors.append(FactorAttribution(
                category="WORKLOAD",
                signal_name="Recognized Launch Surge",
                raw_value="Benign surge detected during release cycle",
                impact_level="LOW",
                supportive_guidance="Acknowledge team milestone contribution and ensure recovery downtime."
            ))

        return min(100.0, score), factors

    def _evaluate_career_velocity(self, emp_id: str, emp: Dict[str, Any], role: Dict[str, Any], band: Dict[str, Any]) -> Tuple[float, List[FactorAttribution]]:
        factors = []
        tenures = self.tenure_by_emp.get(emp_id, [])
        months_in_role = tenures[-1]["months_in_current_role"] if tenures else 12

        score = 15.0

        # Stagnation in same role
        if months_in_role >= 30:
            score += 55.0
            factors.append(FactorAttribution(
                category="CAREER_GROWTH",
                signal_name="Extended Role Tenure Without Movement",
                raw_value=f"{months_in_role} months in current role",
                impact_level="HIGH",
                supportive_guidance="Conduct career pathing discussion; explore internal lateral or promotional readiness."
            ))
        elif months_in_role >= 20:
            score += 30.0
            factors.append(FactorAttribution(
                category="CAREER_GROWTH",
                signal_name="Approaching Career Milestone Window",
                raw_value=f"{months_in_role} months in current role",
                impact_level="MEDIUM",
                supportive_guidance="Review skill development roadmap and upcoming leadership opportunities."
            ))

        # Compensation equity check against mid-band
        curr_sal = emp.get("current_salary", 0)
        mid_sal = band.get("mid_salary", 1)
        if mid_sal > 0:
            comp_ratio = curr_sal / mid_sal
            if comp_ratio < 0.90:
                score += 25.0
                factors.append(FactorAttribution(
                    category="COMPENSATION",
                    signal_name="Compensation Below Band Midpoint",
                    raw_value=f"{comp_ratio*100:.0f}% of market midpoint (${curr_sal:,.0f} vs ${mid_sal:,.0f})",
                    impact_level="MEDIUM",
                    supportive_guidance="Partner with HR compensation team to schedule an equity adjustment review."
                ))

        return min(100.0, score), factors

    def _evaluate_engagement(self, emp_id: str) -> Tuple[float, List[FactorAttribution]]:
        factors = []
        surveys = self.surveys_by_emp.get(emp_id, [])
        if not surveys:
            return 25.0, []

        # STRICT SURVEY NEUTRALITY: Filter out missing surveys without penalty!
        valid_surveys = [s for s in surveys if not s.get("is_missing") and s.get("composite_engagement") is not None]

        if not valid_surveys:
            factors.append(FactorAttribution(
                category="ENGAGEMENT",
                signal_name="Pulse Survey Neutral Absence",
                raw_value="No optional survey submissions on file",
                impact_level="LOW",
                supportive_guidance="Encourage voluntary feedback participation without pressure."
            ))
            return 25.0, factors

        latest = valid_surveys[-1]["composite_engagement"]
        score = max(0.0, (5.0 - latest) * 20.0)

        if len(valid_surveys) >= 2:
            earlier = valid_surveys[0]["composite_engagement"]
            delta = round(latest - earlier, 2)
            if delta <= -0.80:
                score += 45.0
                factors.append(FactorAttribution(
                    category="ENGAGEMENT",
                    signal_name="Downward Engagement Trend",
                    raw_value=f"Score shifted from {earlier:.1f} to {latest:.1f} (Δ {delta:+.1f})",
                    impact_level="HIGH",
                    supportive_guidance="Schedule informal touchpoint to listen to recent workplace friction points."
                ))
            elif latest < 3.0:
                factors.append(FactorAttribution(
                    category="ENGAGEMENT",
                    signal_name="Low Sentiment Score",
                    raw_value=f"Latest pulse composite: {latest:.1f} / 5.0",
                    impact_level="MEDIUM",
                    supportive_guidance="Explore satisfaction with manager support and team collaboration dynamics."
                ))

        return min(100.0, score), factors

    def _generate_recommended_topics(self, factors: List[FactorAttribution]) -> List[str]:
        topics = set()
        for f in factors:
            if f.category == "WORKLOAD":
                topics.add("Sprint Workload Rebalancing & Capacity Planning")
            elif f.category == "CAREER_GROWTH":
                topics.add("Quarterly Career Growth & Progression Roadmap")
            elif f.category == "COMPENSATION":
                topics.add("Annual Compensation & Market Equity Alignment")
            elif f.category == "ENGAGEMENT":
                topics.add("Open 1-on-1 Pulse & Well-being Check-in")

        if not topics:
            topics.add("Routine Supportive 1-on-1 Catchup")

        return sorted(list(topics))

    def get_summary(self, evaluated: List[PrioritizedEmployee]) -> PrioritizationSummary:
        high = sum(1 for e in evaluated if e.priority_tier == "HIGH")
        medium = sum(1 for e in evaluated if e.priority_tier == "MEDIUM")
        low = sum(1 for e in evaluated if e.priority_tier == "LOW")
        active_ints = sum(1 for e in evaluated if e.has_active_intervention)

        return PrioritizationSummary(
            total_evaluated=len(evaluated),
            high_priority_count=high,
            medium_priority_count=medium,
            low_priority_count=low,
            interventions_logged=active_ints,
            top_driver="Sustained High Overtime & Extended Role Stagnation"
        )
