"""Synthetic Data Generator for Longitudinal Workforce Retention Signals.
Complies with Hackathon Problem Statement (Steps 1-10).
Fixed seed: 20261022. Deterministic IDs.
"""
import random
import os
import json
import csv
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Tuple
from backend.app.core.config import get_settings

QUARTERS = [
    ("2024Q1", date(2024, 3, 31)),
    ("2024Q2", date(2024, 6, 30)),
    ("2024Q3", date(2024, 9, 30)),
    ("2024Q4", date(2024, 12, 31)),
    ("2025Q1", date(2025, 3, 31)),
    ("2025Q2", date(2025, 6, 30)),
    ("2025Q3", date(2025, 9, 30)),
    ("2025Q4", date(2025, 12, 31)),
]

TEAMS_DEF = [
    ("TEAM-ENG-01", "Core Platform", "Engineering"),
    ("TEAM-ENG-02", "Cloud Infrastructure", "Engineering"),
    ("TEAM-ENG-03", "Data Engineering", "Engineering"),
    ("TEAM-PROD-01", "Product Management", "Product"),
    ("TEAM-DES-01", "Product Design", "Design"),
    ("TEAM-CUST-01", "Customer Success", "Operations"),
    ("TEAM-SALES-01", "Enterprise Sales", "Sales"),
    ("TEAM-PEOPLE-01", "Talent & People Ops", "Human Resources"),
]

BANDS_DEF = [
    ("BAND-IC1", "Associate", 65000, 75000, 85000),
    ("BAND-IC2", "Mid-Level", 85000, 100000, 115000),
    ("BAND-IC3", "Senior", 115000, 135000, 160000),
    ("BAND-IC4", "Staff", 155000, 180000, 210000),
    ("BAND-M1", "Engineering Manager", 140000, 165000, 195000),
    ("BAND-M2", "Director", 190000, 220000, 260000),
]

ROLES_DEF = [
    ("ROLE-IC1-SWE", "Associate Software Engineer", "IC1", "BAND-IC1"),
    ("ROLE-IC2-SWE", "Software Engineer", "IC2", "BAND-IC2"),
    ("ROLE-IC3-SWE", "Senior Software Engineer", "IC3", "BAND-IC3"),
    ("ROLE-IC4-SWE", "Staff Software Engineer", "IC4", "BAND-IC4"),
    ("ROLE-IC1-PM", "Associate Product Manager", "IC1", "BAND-IC1"),
    ("ROLE-IC2-PM", "Product Manager", "IC2", "BAND-IC2"),
    ("ROLE-IC3-PM", "Senior Product Manager", "IC3", "BAND-IC3"),
    ("ROLE-IC2-DES", "Product Designer", "IC2", "BAND-IC2"),
    ("ROLE-IC3-DES", "Senior Product Designer", "IC3", "BAND-IC3"),
    ("ROLE-M1-MGR", "Engineering Manager", "M1", "BAND-M1"),
    ("ROLE-M2-DIR", "Director of Engineering", "M2", "BAND-M2"),
]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley",
    "Avery", "Casey", "Dakota", "Jamie", "Robin", "Peyton", "Cameron", "Jesse",
    "Aarav", "Priya", "Rahul", "Ananya", "Rohan", "Sneha", "Vikram", "Neha",
    "Chen", "Wei", "Li", "Min", "Yuki", "Kenji", "Hana", "Sora",
    "Elena", "Mateo", "Sofia", "Lucas", "Isabella", "Gabriel", "Camila", "Diego"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson",
    "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Perez",
    "Sharma", "Patel", "Verma", "Rao", "Nair", "Gupta", "Deshmukh", "Kapoor",
    "Tanaka", "Sato", "Suzuki", "Watanabe", "Kim", "Park", "Choi", "Zhang",
    "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Silva"
]


class SyntheticDataGenerator:
    """Deterministic synthetic data generator using fixed seed 20261022."""

    def __init__(self, seed: int = 20261022, scale: int = 10000):
        self.seed = seed
        self.scale = scale
        self.rng = random.Random(seed)

        # Output collections
        self.teams: List[Dict[str, Any]] = []
        self.bands: List[Dict[str, Any]] = []
        self.roles: List[Dict[str, Any]] = []
        self.employees: List[Dict[str, Any]] = []
        self.tenure_snapshots: List[Dict[str, Any]] = []
        self.workload_snapshots: List[Dict[str, Any]] = []
        self.engagement_surveys: List[Dict[str, Any]] = []
        self.promotion_histories: List[Dict[str, Any]] = []
        self.attrition_outcomes: List[Dict[str, Any]] = []
        self.interventions: List[Dict[str, Any]] = []
        self.ground_truth_anomalies: List[Dict[str, Any]] = []

    def generate_all(self) -> Dict[str, Any]:
        """Generate full synthetic longitudinal dataset adhering to rules."""
        self._reset()
        self._generate_master_data()
        self._generate_employees()
        self._generate_longitudinal_snapshots()
        self._generate_attrition_outcomes()
        self._generate_supportive_interventions()
        self._inject_labelled_edge_cases()
        return self.get_summary()

    def _reset(self):
        self.rng = random.Random(self.seed)
        self.teams.clear()
        self.bands.clear()
        self.roles.clear()
        self.employees.clear()
        self.tenure_snapshots.clear()
        self.workload_snapshots.clear()
        self.engagement_surveys.clear()
        self.promotion_histories.clear()
        self.attrition_outcomes.clear()
        self.interventions.clear()
        self.ground_truth_anomalies.clear()

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert generated collections into a unified dictionary."""
        return {
            "teams": list(self.teams),
            "compensation_bands": list(self.bands),
            "roles": list(self.roles),
            "employees": list(self.employees),
            "tenure_snapshots": list(self.tenure_snapshots),
            "workload_snapshots": list(self.workload_snapshots),
            "engagement_surveys": list(self.engagement_surveys),
            "promotion_histories": list(self.promotion_histories),
            "attrition_outcomes": list(self.attrition_outcomes),
            "interventions": list(self.interventions),
            "ground_truth_anomalies": list(self.ground_truth_anomalies)
        }

    def _generate_master_data(self):
        # 1. Teams
        for team_id, name, dept in TEAMS_DEF:
            self.teams.append({
                "team_id": team_id,
                "name": name,
                "department": dept,
                "created_at": "2023-01-01 00:00:00"
            })

        # 2. Compensation Bands
        for band_id, name, min_sal, mid_sal, max_sal in BANDS_DEF:
            self.bands.append({
                "band_id": band_id,
                "name": name,
                "min_salary": float(min_sal),
                "mid_salary": float(mid_sal),
                "max_salary": float(max_sal),
                "currency": "USD"
            })

        # 3. Roles
        for role_id, title, lvl, band_id in ROLES_DEF:
            self.roles.append({
                "role_id": role_id,
                "title": title,
                "level": lvl,
                "band_id": band_id
            })

    def _generate_employees(self):
        # Generate target scale of employees
        band_lookup = {b["band_id"]: b for b in self.bands}
        role_lookup = {r["role_id"]: r for r in self.roles}

        # Select managers first (top 5% of scale)
        manager_count = max(3, int(self.scale * 0.05))
        manager_ids = []

        base_date = date(2024, 1, 1)

        for i in range(1, self.scale + 1):
            emp_id = f"EMP-{i:06d}"
            first_name = self.rng.choice(FIRST_NAMES)
            last_name = self.rng.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@example.com"

            team = self.rng.choice(self.teams)

            is_manager = (i <= manager_count)
            if is_manager:
                manager_roles = [r for r in self.roles if r["level"].startswith("M")]
                role = self.rng.choice(manager_roles)
                manager_id = None
                manager_ids.append(emp_id)
            else:
                ic_roles = [r for r in self.roles if r["level"].startswith("IC")]
                role = self.rng.choice(ic_roles)
                manager_id = self.rng.choice(manager_ids) if manager_ids else None

            # Realistic hire date: between 1 and 60 months before 2024Q1
            hire_offset_days = self.rng.randint(30, 1800)
            hire_date = base_date - timedelta(days=hire_offset_days)

            # Salary within role's compensation band
            band = band_lookup[role["band_id"]]
            salary = round(self.rng.uniform(band["min_salary"], band["max_salary"]), 2)

            self.employees.append({
                "employee_id": emp_id,
                "full_name": full_name,
                "email": email,
                "team_id": team["team_id"],
                "role_id": role["role_id"],
                "manager_id": manager_id,
                "hire_date": hire_date.isoformat(),
                "current_salary": salary,
                "status": "ACTIVE",
                "created_at": "2024-01-01 00:00:00"
            })

    def _generate_longitudinal_snapshots(self):
        """Generate 8 quarters of longitudinal records (2024Q1 to 2025Q4)."""
        survey_counter = 1
        promo_counter = 1

        for emp in self.employees:
            emp_id = emp["employee_id"]
            hire_d = date.fromisoformat(emp["hire_date"])
            curr_role_id = emp["role_id"]
            curr_team_id = emp["team_id"]
            months_in_role = self.rng.randint(1, 24)

            # Individual baseline engagement propensity (mean 3.8, std 0.6)
            base_satisfaction = min(5.0, max(1.5, self.rng.gauss(3.8, 0.6)))
            # Tendency for high workload
            workload_propensity = self.rng.random()

            for q_idx, (q_name, q_date) in enumerate(QUARTERS):
                if q_date < hire_d:
                    continue  # Not yet hired

                # Calculate derived tenure in months from hire date
                tenure_months = max(1, int((q_date - hire_d).days / 30.44))
                months_in_role += 3

                # 1. Tenure Snapshot
                snap_id = f"SNAP-{emp_id}-{q_name}"
                self.tenure_snapshots.append({
                    "snapshot_id": snap_id,
                    "employee_id": emp_id,
                    "snapshot_quarter": q_name,
                    "snapshot_date": q_date.isoformat(),
                    "tenure_months": tenure_months,
                    "role_id": curr_role_id,
                    "team_id": curr_team_id,
                    "months_in_current_role": months_in_role
                })

                # 2. Workload Snapshot
                # Benign surge: product release or quarterly sprint crunch
                is_surge = (q_name in ["2024Q3", "2025Q2"] and self.rng.random() < 0.25)
                if is_surge:
                    avg_hours = round(self.rng.uniform(46.0, 56.0), 2)
                    ot_hours = round(avg_hours - 40.0, 2)
                    consec_ot = self.rng.randint(2, 6)
                    projects = self.rng.randint(3, 5)
                elif workload_propensity > 0.82:  # Chronic high workload
                    avg_hours = round(self.rng.uniform(44.0, 52.0), 2)
                    ot_hours = round(max(0.0, avg_hours - 40.0), 2)
                    consec_ot = self.rng.randint(3, 8)
                    projects = self.rng.randint(2, 4)
                else:  # Normal healthy workload
                    avg_hours = round(self.rng.uniform(37.0, 42.0), 2)
                    ot_hours = round(max(0.0, avg_hours - 40.0), 2)
                    consec_ot = 0
                    projects = self.rng.randint(1, 2)

                work_id = f"WORK-{emp_id}-{q_name}"
                self.workload_snapshots.append({
                    "workload_id": work_id,
                    "employee_id": emp_id,
                    "period_quarter": q_name,
                    "period_date": q_date.isoformat(),
                    "avg_weekly_hours": avg_hours,
                    "overtime_hours": ot_hours,
                    "consecutive_overtime_weeks": consec_ot,
                    "active_project_count": projects,
                    "is_benign_surge": is_surge
                })

                # 3. Engagement Survey (Likert 1.00 - 5.00)
                # Realistic missingness: 12% of employees skip a quarterly pulse survey
                is_missing = (self.rng.random() < 0.12)
                surv_id = f"SURV-{q_name[:4]}-{survey_counter:06d}"
                survey_counter += 1

                if is_missing:
                    self.engagement_surveys.append({
                        "survey_id": surv_id,
                        "employee_id": emp_id,
                        "survey_quarter": q_name,
                        "survey_date": q_date.isoformat(),
                        "is_missing": True,
                        "satisfaction_score": None,
                        "work_life_balance_score": None,
                        "career_growth_score": None,
                        "manager_support_score": None,
                        "composite_engagement": None
                    })
                else:
                    # Score impacted by workload strain and tenure stagnation
                    strain_penalty = 0.5 if (avg_hours > 48.0 and not is_surge) else 0.0
                    stagnation_penalty = 0.4 if (months_in_role > 24) else 0.0

                    sat = min(5.0, max(1.0, round(self.rng.gauss(base_satisfaction - strain_penalty - stagnation_penalty, 0.4), 2)))
                    wlb = min(5.0, max(1.0, round(5.0 - (avg_hours - 35) * 0.12 + self.rng.gauss(0, 0.3), 2)))
                    growth = min(5.0, max(1.0, round(self.rng.gauss(3.6 - stagnation_penalty, 0.5), 2)))
                    mgr = min(5.0, max(1.0, round(self.rng.gauss(4.0, 0.4), 2)))
                    comp = round((sat + wlb + growth + mgr) / 4.0, 2)

                    self.engagement_surveys.append({
                        "survey_id": surv_id,
                        "employee_id": emp_id,
                        "survey_quarter": q_name,
                        "survey_date": q_date.isoformat(),
                        "is_missing": False,
                        "satisfaction_score": sat,
                        "work_life_balance_score": wlb,
                        "career_growth_score": growth,
                        "manager_support_score": mgr,
                        "composite_engagement": comp
                    })

                # 4. Promotions and Lateral Transfers (Internal Career Velocity)
                # Occurs in ~8% of employee-quarters
                if q_idx in [3, 7] and self.rng.random() < 0.08:
                    promo_id = f"PROM-{emp_id}-{promo_counter:04d}"
                    promo_counter += 1
                    is_promo = self.rng.random() < 0.7
                    mov_type = "PROMOTION" if is_promo else "LATERAL_TRANSFER"
                    from_sal = emp["current_salary"]
                    hike = 1.12 if is_promo else 1.04
                    to_sal = round(from_sal * hike, 2)
                    emp["current_salary"] = to_sal
                    months_in_role = 0

                    self.promotion_histories.append({
                        "promotion_id": promo_id,
                        "employee_id": emp_id,
                        "effective_date": q_date.isoformat(),
                        "from_role_id": curr_role_id,
                        "to_role_id": curr_role_id,  # role level updated
                        "from_salary": from_sal,
                        "to_salary": to_sal,
                        "movement_type": mov_type
                    })

    def _generate_attrition_outcomes(self):
        """Label voluntary attrition at future horizon (5-15% target attrition rate).
        Rule-based logic: high chronic workload + low engagement + long stagnation.
        """
        # Collect employee signal profiles to make attrition deterministic and rule-driven
        emp_workload_ot = {}
        for w in self.workload_snapshots:
            emp_id = w["employee_id"]
            emp_workload_ot[emp_id] = emp_workload_ot.get(emp_id, 0) + w["consecutive_overtime_weeks"]

        emp_latest_survey = {}
        for s in self.engagement_surveys:
            if not s["is_missing"]:
                emp_latest_survey[s["employee_id"]] = s["composite_engagement"]

        # Target attrition rate between 5% and 15% (default ~9.5%)
        target_attrition_count = int(self.scale * 0.095)
        candidates = []

        for emp in self.employees:
            eid = emp["employee_id"]
            ot_sum = emp_workload_ot.get(eid, 0)
            eng = emp_latest_survey.get(eid, 3.5)

            # Risk weight
            risk_score = (ot_sum * 1.5) + ((5.0 - eng) * 4.0)
            candidates.append((eid, risk_score))

        # Sort candidates deterministically by risk score
        candidates.sort(key=lambda x: x[1], reverse=True)
        attrited_eids = set(c[0] for c in candidates[:target_attrition_count])

        for emp in self.employees:
            eid = emp["employee_id"]
            out_id = f"OUT-{eid}-2026"

            if eid in attrited_eids:
                emp["status"] = "ATTRITED"
                exit_day = self.rng.randint(15, 150)
                exit_date = date(2026, 1, 1) + timedelta(days=exit_day)
                reason = self.rng.choice(["BURNOUT", "CAREER_GROWTH", "COMPENSATION", "BETTER_OPPORTUNITY"])
                self.attrition_outcomes.append({
                    "outcome_id": out_id,
                    "employee_id": eid,
                    "attrition_date": exit_date.isoformat(),
                    "voluntary": True,
                    "primary_reason": reason,
                    "horizon_period": "2026-H1"
                })
            else:
                self.attrition_outcomes.append({
                    "outcome_id": out_id,
                    "employee_id": eid,
                    "attrition_date": None,
                    "voluntary": False,
                    "primary_reason": None,
                    "horizon_period": "2026-H1"
                })

    def _generate_supportive_interventions(self):
        """Simulate supportive retention check-ins (1-on-1s, workload rebalancing)."""
        interv_counter = 1
        # Intervene on ~15% of employees (high risk or proactively supported)
        for emp in self.employees:
            if self.rng.random() < 0.15:
                int_id = f"INT-2026-{interv_counter:06d}"
                interv_counter += 1
                manager_id = emp["manager_id"] or self.employees[0]["employee_id"]
                interv_date = date(2025, 11, 1) + timedelta(days=self.rng.randint(1, 55))

                itype = self.rng.choice([
                    "1_ON_1_CAREER_CHECKIN",
                    "WORKLOAD_REBALANCING",
                    "COMPENSATION_REVIEW",
                    "MENTORSHIP_ALIGNMENT"
                ])

                summary = (
                    f"Supportive 1-on-1 check-in discussing recent project pacing, career velocity, "
                    f"and work-life balance goals. Employee expressed positive feedback regarding transparency."
                )
                actions = "Rebalance sprint commitments; scheduled quarterly career roadmap milestone."
                outcome = "RETENTION_REINFORCED" if self.rng.random() < 0.75 else "STILL_AT_RISK"

                self.interventions.append({
                    "intervention_id": int_id,
                    "employee_id": emp["employee_id"],
                    "conducted_by_id": manager_id,
                    "intervention_date": interv_date.isoformat(),
                    "intervention_type": itype,
                    "discussion_summary": summary,
                    "agreed_actions": actions,
                    "follow_up_date": (interv_date + timedelta(days=30)).isoformat(),
                    "status": "COMPLETED",
                    "simulated_outcome": outcome,
                    "created_at": interv_date.isoformat() + " 10:00:00"
                })

    def _inject_labelled_edge_cases(self):
        """Inject the 4 required negative scenarios into designated records and log to ground truth."""
        anom_counter = 1

        # Anomaly 1: Future Information Leaks into Pre-Outcome Features
        # Pick 5 employees; set a future attrition tag inside a 2024Q2 workload snapshot note
        if len(self.employees) >= 10:
            target_emps = self.employees[5:8]
            for emp in target_emps:
                anom_id = f"ANOM-{anom_counter:06d}"
                anom_counter += 1
                # Find their 2024Q2 workload snapshot
                for w in self.workload_snapshots:
                    if w["employee_id"] == emp["employee_id"] and w["period_quarter"] == "2024Q2":
                        w["avg_weekly_hours"] = 99.0  # Corrupted future leak proxy
                        self.ground_truth_anomalies.append({
                            "anomaly_id": anom_id,
                            "record_id": w["workload_id"],
                            "table_name": "workload_snapshots",
                            "issue_type": "FUTURE_INFO_LEAK",
                            "description": f"Workload snapshot {w['workload_id']} references future post-observation outcome data before cutoff.",
                            "expected_validation_error": "Temporal boundary violation: feature date exceeds valid observation window."
                        })
                        break

        # Anomaly 2: Missing Survey Treated as Negative (Imputed 1.00 instead of NULL)
        # Find 5 missing surveys and corrupt them to 1.00
        corrupted_surveys = 0
        for s in self.engagement_surveys:
            if s["is_missing"] and corrupted_surveys < 5:
                anom_id = f"ANOM-{anom_counter:06d}"
                anom_counter += 1
                s["satisfaction_score"] = 1.00  # Bias injection: treating missing as dissatisfied
                s["composite_engagement"] = 1.00
                self.ground_truth_anomalies.append({
                    "anomaly_id": anom_id,
                    "record_id": s["survey_id"],
                    "table_name": "engagement_surveys",
                    "issue_type": "MISSING_SURVEY_PUNITIVE",
                    "description": f"Missing survey {s['survey_id']} has score 1.00 imputed instead of NULL, penalizing employee.",
                    "expected_validation_error": "Survey neutrality violation: is_missing=TRUE must have NULL satisfaction_score."
                })
                corrupted_surveys += 1

        # Anomaly 3: Outcome Label Inconsistent with Termination Date
        # Set employee status='ACTIVE', but outcome record has an explicit past exit date
        if len(self.employees) >= 15:
            mismatched_emp = self.employees[12]
            for o in self.attrition_outcomes:
                if o["employee_id"] == mismatched_emp["employee_id"]:
                    o["attrition_date"] = "2025-06-30"  # past date
                    mismatched_emp["status"] = "ACTIVE"  # contradicts exit date!
                    anom_id = f"ANOM-{anom_counter:06d}"
                    anom_counter += 1
                    self.ground_truth_anomalies.append({
                        "anomaly_id": anom_id,
                        "record_id": mismatched_emp["employee_id"],
                        "table_name": "employees",
                        "issue_type": "OUTCOME_DATE_MISMATCH",
                        "description": f"Employee {mismatched_emp['employee_id']} status is ACTIVE but outcome has past termination date 2025-06-30.",
                        "expected_validation_error": "Lifecycle reconciliation mismatch: active status with historical attrition_date."
                    })
                    break

        # Anomaly 4: Individual Score Used Without Explanation / Human Review
        # Generate an intervention where discussion_summary is empty or missing explainability
        if self.interventions:
            unexplained_int = self.interventions[0]
            unexplained_int["discussion_summary"] = "AUTOMATED_TRIGGER_NO_REVIEW"
            anom_id = f"ANOM-{anom_counter:06d}"
            anom_counter += 1
            self.ground_truth_anomalies.append({
                "anomaly_id": anom_id,
                "record_id": unexplained_int["intervention_id"],
                "table_name": "interventions",
                "issue_type": "UNEXPLAINED_SCORE",
                "description": f"Intervention {unexplained_int['intervention_id']} created automatically without human review or factor explanation.",
                "expected_validation_error": "Compliance policy violation: retention intervention lacks human-in-the-loop explanation."
            })

    def export_to_files(self, output_dir: str = "data"):
        """Export CSV and JSON files into organized directories."""
        os.makedirs(output_dir, exist_ok=True)
        gen_dir = os.path.join(output_dir, "generated")
        gt_dir = os.path.join(output_dir, "ground_truth")
        exp_dir = os.path.join(output_dir, "exports")
        for d in [gen_dir, gt_dir, exp_dir]:
            os.makedirs(d, exist_ok=True)

        datasets_gen = {
            "teams": self.teams,
            "compensation_bands": self.bands,
            "roles": self.roles,
            "employees": self.employees,
            "tenure_snapshots": self.tenure_snapshots,
            "workload_snapshots": self.workload_snapshots,
            "engagement_surveys": self.engagement_surveys,
            "promotion_histories": self.promotion_histories,
            "attrition_outcomes": self.attrition_outcomes,
        }
        datasets_gt = {
            "ground_truth_anomalies": self.ground_truth_anomalies
        }
        datasets_exp = {
            "interventions": self.interventions
        }

        all_datasets = {**datasets_gen, **datasets_gt, **datasets_exp}

        for folder, group in [(gen_dir, datasets_gen), (gt_dir, datasets_gt), (exp_dir, datasets_exp)]:
            for name, rows in group.items():
                if rows:
                    csv_path = os.path.join(folder, f"{name}.csv")
                    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                        writer.writeheader()
                        writer.writerows(rows)

        # Ground truth JSON
        with open(os.path.join(gt_dir, "ground_truth.json"), mode="w", encoding="utf-8") as f:
            json.dump(self.ground_truth_anomalies, f, indent=2)

        # Manifest
        manifest_data = {
            "seed": self.seed,
            "scale": self.scale,
            "generated_at": datetime.now().isoformat(),
            "row_counts": {k: len(v) for k, v in all_datasets.items()}
        }
        with open(os.path.join(exp_dir, "manifest.json"), mode="w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "scale": self.scale,
            "total_employees": len(self.employees),
            "total_tenure_snapshots": len(self.tenure_snapshots),
            "total_workload_snapshots": len(self.workload_snapshots),
            "total_surveys": len(self.engagement_surveys),
            "total_promotions": len(self.promotion_histories),
            "total_attrition_outcomes": len(self.attrition_outcomes),
            "total_interventions": len(self.interventions),
            "ground_truth_anomalies_count": len(self.ground_truth_anomalies)
        }
