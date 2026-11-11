"""Synthetic Data Generator & Seeder for Employee Retention Support System.
Generates 10,000 employees over 24 months with fixed seed 20261022.
"""
import random
import sys
import argparse
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.core.config import get_settings
from backend.app.database.session import SessionLocal
from backend.app.models import (
    CompensationBand, Role, Team, Employee, TeamMembershipHistory,
    TenureSnapshot, WorkloadSnapshot, EngagementSurvey, PromotionHistory,
    AttritionOutcome, Intervention, InterventionEvent, AppUser, UserRole
)

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


class DatabaseSeeder:
    def __init__(self, seed: int = 20261022, scale: int = 10000):
        self.seed = seed
        self.scale = scale
        self.rng = random.Random(seed)

    def run(self, db: Session):
        print(f"[*] Starting synthetic data seeding (Scale: {self.scale}, Seed: {self.seed})...")

        # 1. Seed Master Reference Data
        self._seed_reference_data(db)

        # 2. Seed Employees
        employees = self._seed_employees(db)

        # 3. Seed Longitudinal Records & Team History
        self._seed_longitudinal_records(db, employees)

        # 4. Seed Attrition Outcomes (Future ground truth)
        self._seed_attrition_outcomes(db, employees)

        # 5. Seed Interventions & Events
        self._seed_interventions(db, employees)

        # 6. Seed App Users
        self._seed_app_users(db, employees)

        print(f"[SUCCESS] Synthetic seeding completed successfully.")

    def _seed_reference_data(self, db: Session):
        # Bands
        bands = [
            CompensationBand(
                band_id=b_id, name=name, min_salary=min_s, mid_salary=mid_s, max_salary=max_s, currency="USD"
            )
            for b_id, name, min_s, mid_s, max_s in BANDS_DEF
        ]
        db.bulk_save_objects(bands)

        # Teams
        teams = [Team(team_id=t_id, name=name, department=dept) for t_id, name, dept in TEAMS_DEF]
        db.bulk_save_objects(teams)

        # Roles
        roles = [Role(role_id=r_id, title=title, level=lvl, band_id=b_id) for r_id, title, lvl, b_id in ROLES_DEF]
        db.bulk_save_objects(roles)
        db.commit()
        print(f"  [+] Reference master data seeded: {len(bands)} bands, {len(teams)} teams, {len(roles)} roles.")

    def _seed_employees(self, db: Session) -> List[Dict[str, Any]]:
        band_lookup = {b[0]: b for b in BANDS_DEF}
        manager_count = max(3, int(self.scale * 0.05))
        manager_ids = []

        base_date = date(2024, 1, 1)
        employees_data = []

        for i in range(1, self.scale + 1):
            emp_id = f"EMP-{i:06d}"
            fn = self.rng.choice(FIRST_NAMES)
            ln = self.rng.choice(LAST_NAMES)
            email = f"{fn.lower()}.{ln.lower()}.{i}@example.com"
            team_id = self.rng.choice(TEAMS_DEF)[0]

            is_mgr = (i <= manager_count)
            if is_mgr:
                role_id = self.rng.choice([r[0] for r in ROLES_DEF if r[2].startswith("M")])
                mgr_id = None
                manager_ids.append(emp_id)
            else:
                role_id = self.rng.choice([r[0] for r in ROLES_DEF if r[2].startswith("IC")])
                mgr_id = self.rng.choice(manager_ids) if manager_ids else None

            # Role's compensation band
            role_def = next(r for r in ROLES_DEF if r[0] == role_id)
            band_def = band_lookup[role_def[3]]
            salary = round(self.rng.uniform(band_def[2], band_def[4]), 2)

            hire_offset_days = self.rng.randint(30, 1800)
            hire_d = base_date - timedelta(days=hire_offset_days)

            employees_data.append({
                "employee_id": emp_id,
                "first_name": fn,
                "last_name": ln,
                "email": email,
                "hire_date": hire_d,
                "current_role_id": role_id,
                "current_team_id": team_id,
                "current_salary": salary,
                "manager_id": mgr_id,
                "status": "ACTIVE",
                "created_at": datetime(2024, 1, 1)
            })

        emp_objs = [Employee(**e) for e in employees_data]
        db.bulk_save_objects(emp_objs)
        db.commit()
        print(f"  [+] Employees seeded: {len(emp_objs)} employees.")
        return employees_data

    def _seed_longitudinal_records(self, db: Session, employees: List[Dict[str, Any]]):
        tenure_snapshots = []
        workload_snapshots = []
        surveys = []
        promotions = []
        memberships = []

        survey_seq = 1
        promo_seq = 1
        mem_seq = 1

        for emp in employees:
            eid = emp["employee_id"]
            hire_d = emp["hire_date"]
            curr_role = emp["current_role_id"]
            curr_team = emp["current_team_id"]
            months_in_role = self.rng.randint(1, 24)

            # Initial team membership
            mem_id = f"MEM-{eid}-{mem_seq:04d}"
            mem_seq += 1
            memberships.append(TeamMembershipHistory(
                membership_id=mem_id,
                employee_id=eid,
                team_id=curr_team,
                role_id=curr_role,
                effective_start_date=hire_d,
                effective_end_date=None,
                is_current=True,
                transfer_reason="HIRE"
            ))

            for q_idx, (q_name, q_date) in enumerate(QUARTERS):
                if q_date < hire_d:
                    continue

                tenure_mos = max(1, int((q_date - hire_d).days / 30.44))
                months_in_role += 3

                # 1. Tenure Snapshot
                snap_id = f"SNAP-{eid}-{q_name}"
                tenure_snapshots.append(TenureSnapshot(
                    snapshot_id=snap_id,
                    employee_id=eid,
                    snapshot_quarter=q_name,
                    snapshot_date=q_date,
                    tenure_months=tenure_mos,
                    role_id=curr_role,
                    team_id=curr_team,
                    months_in_current_role=months_in_role
                ))

                # 2. Workload Snapshot (with benign surges)
                is_benign = (q_name in ["2024Q3", "2025Q2"] and self.rng.random() < 0.20)
                if is_benign:
                    avg_hrs = round(self.rng.uniform(47.0, 56.0), 2)
                    ot_hrs = round(avg_hrs - 40.0, 2)
                    consec_ot = self.rng.randint(2, 6)
                    projects = self.rng.randint(3, 5)
                elif self.rng.random() < 0.15:  # Chronic strain
                    avg_hrs = round(self.rng.uniform(46.0, 53.0), 2)
                    ot_hrs = round(avg_hrs - 40.0, 2)
                    consec_ot = self.rng.randint(4, 9)
                    projects = self.rng.randint(2, 4)
                else:  # Normal
                    avg_hrs = round(self.rng.uniform(37.0, 42.0), 2)
                    ot_hrs = round(max(0.0, avg_hrs - 40.0), 2)
                    consec_ot = 0
                    projects = self.rng.randint(1, 2)

                work_id = f"WORK-{eid}-{q_name}"
                workload_snapshots.append(WorkloadSnapshot(
                    workload_id=work_id,
                    employee_id=eid,
                    period_quarter=q_name,
                    period_date=q_date,
                    avg_weekly_hours=avg_hrs,
                    overtime_hours=ot_hrs,
                    consecutive_overtime_weeks=consec_ot,
                    active_project_count=projects,
                    is_benign_surge=is_benign
                ))

                # 3. Engagement Survey (Voluntary pulse with neutrality)
                is_skip = (self.rng.random() < 0.12)
                surv_id = f"SURV-{q_name[:4]}-{survey_seq:06d}"
                survey_seq += 1

                if is_skip:
                    # STRICT SURVEY NEUTRALITY: Scores MUST be NULL
                    surveys.append(EngagementSurvey(
                        survey_id=surv_id,
                        employee_id=eid,
                        survey_quarter=q_name,
                        survey_date=q_date,
                        is_missing=True,
                        satisfaction_score=None,
                        work_life_balance_score=None,
                        career_growth_score=None,
                        manager_support_score=None,
                        composite_engagement=None
                    ))
                else:
                    sat = min(5.0, max(1.0, round(self.rng.gauss(3.8, 0.5), 2)))
                    wlb = min(5.0, max(1.0, round(5.0 - (avg_hrs - 36) * 0.12, 2)))
                    growth = min(5.0, max(1.0, round(self.rng.gauss(3.7, 0.4), 2)))
                    mgr = min(5.0, max(1.0, round(self.rng.gauss(4.0, 0.4), 2)))
                    comp = round((sat + wlb + growth + mgr) / 4.0, 2)
                    surveys.append(EngagementSurvey(
                        survey_id=surv_id,
                        employee_id=eid,
                        survey_quarter=q_name,
                        survey_date=q_date,
                        is_missing=False,
                        satisfaction_score=sat,
                        work_life_balance_score=wlb,
                        career_growth_score=growth,
                        manager_support_score=mgr,
                        composite_engagement=comp
                    ))

                # 4. Promotions and Team Transfers
                if q_idx in [3, 7] and self.rng.random() < 0.08:
                    pr_id = f"PROM-{eid}-{promo_seq:04d}"
                    promo_seq += 1
                    is_p = self.rng.random() < 0.7
                    mov_t = "PROMOTION" if is_p else "LATERAL_TRANSFER"
                    from_s = emp["current_salary"]
                    to_s = round(from_s * (1.12 if is_p else 1.04), 2)
                    promotions.append(PromotionHistory(
                        promotion_id=pr_id,
                        employee_id=eid,
                        effective_date=q_date,
                        from_role_id=curr_role,
                        to_role_id=curr_role,
                        from_salary=from_s,
                        to_salary=to_s,
                        movement_type=mov_t
                    ))

        # Bulk commit in batches
        db.bulk_save_objects(memberships)
        db.bulk_save_objects(tenure_snapshots)
        db.bulk_save_objects(workload_snapshots)
        db.bulk_save_objects(surveys)
        db.bulk_save_objects(promotions)
        db.commit()
        print(f"  [+] Longitudinal records seeded: {len(tenure_snapshots)} tenure snaps, {len(workload_snapshots)} workload snaps, {len(surveys)} surveys.")

    def _seed_attrition_outcomes(self, db: Session, employees: List[Dict[str, Any]]):
        # 5-15% voluntary attrition (target: 9.5%)
        target_count = int(self.scale * 0.095)
        attrited_indices = set(self.rng.sample(range(len(employees)), target_count))

        outcomes = []
        for idx, emp in enumerate(employees):
            eid = emp["employee_id"]
            out_id = f"OUT-{eid}-2026"
            if idx in attrited_indices:
                exit_d = date(2026, 1, 1) + timedelta(days=self.rng.randint(15, 150))
                reason = self.rng.choice(["BURNOUT", "CAREER_GROWTH", "COMPENSATION", "BETTER_OPPORTUNITY"])
                outcomes.append(AttritionOutcome(
                    outcome_id=out_id,
                    employee_id=eid,
                    attrition_date=exit_d,
                    voluntary=True,
                    primary_reason=reason,
                    horizon_period="2026-H1"
                ))
            else:
                outcomes.append(AttritionOutcome(
                    outcome_id=out_id,
                    employee_id=eid,
                    attrition_date=None,
                    voluntary=False,
                    primary_reason=None,
                    horizon_period="2026-H1"
                ))

        db.bulk_save_objects(outcomes)
        db.commit()
        print(f"  [+] Attrition outcomes seeded: {len(outcomes)} records (Target Attrition: {target_count/len(employees)*100:.1f}%).")

    def _seed_interventions(self, db: Session, employees: List[Dict[str, Any]]):
        interventions = []
        events = []
        int_seq = 1
        ev_seq = 1

        # Intervene on ~12% of workforce
        for emp in employees:
            if self.rng.random() < 0.12:
                int_id = f"INT-2026-{int_seq:06d}"
                int_seq += 1
                mgr_id = emp["manager_id"] or employees[0]["employee_id"]
                int_d = date(2025, 11, 1) + timedelta(days=self.rng.randint(1, 55))

                itype = self.rng.choice([
                    "1_ON_1_CAREER_CHECKIN",
                    "WORKLOAD_REBALANCING",
                    "COMPENSATION_REVIEW",
                    "MENTORSHIP_ALIGNMENT"
                ])

                interventions.append(Intervention(
                    intervention_id=int_id,
                    employee_id=emp["employee_id"],
                    conducted_by_id=mgr_id,
                    intervention_date=int_d,
                    intervention_type=itype,
                    discussion_summary="Supportive retention 1-on-1 discussing capacity, workload pacing, and progression roadmap.",
                    agreed_actions="Rebalance sprint commitments; scheduled quarterly milestone check-in.",
                    follow_up_date=int_d + timedelta(days=30),
                    status="COMPLETED",
                    simulated_outcome="RETENTION_REINFORCED"
                ))

                # Event log
                ev_id = f"INTEV-2026-{ev_seq:06d}"
                ev_seq += 1
                events.append(InterventionEvent(
                    event_id=ev_id,
                    intervention_id=int_id,
                    event_type="CREATED",
                    event_timestamp=datetime(2025, 11, int_d.day, 10, 0, 0),
                    actor_id=mgr_id,
                    notes="Logged supportive 1-on-1 retention session."
                ))

        db.bulk_save_objects(interventions)
        db.bulk_save_objects(events)
        db.commit()
        print(f"  [+] Interventions & event logs seeded: {len(interventions)} interventions.")

    def _seed_app_users(self, db: Session, employees: List[Dict[str, Any]]):
        # Seed 4 standard role users for RBAC testing
        users = [
            AppUser(
                user_id="USR-000001",
                username="hr_partner_1",
                email="hr.partner@example.com",
                hashed_password="pbkdf2_sha256$260000$mock_hash_for_testing",
                role=UserRole.HR_PARTNER.value,
                employee_id=employees[0]["employee_id"],
                is_active=True
            ),
            AppUser(
                user_id="USR-000002",
                username="manager_apollo",
                email="manager.apollo@example.com",
                hashed_password="pbkdf2_sha256$260000$mock_hash_for_testing",
                role=UserRole.MANAGER.value,
                employee_id=employees[1]["employee_id"] if len(employees) > 1 else None,
                is_active=True
            ),
            AppUser(
                user_id="USR-000003",
                username="sys_admin",
                email="admin@example.com",
                hashed_password="pbkdf2_sha256$260000$mock_hash_for_testing",
                role=UserRole.SYSTEM_ADMIN.value,
                is_active=True
            ),
            AppUser(
                user_id="USR-000004",
                username="compliance_auditor",
                email="auditor@example.com",
                hashed_password="pbkdf2_sha256$260000$mock_hash_for_testing",
                role=UserRole.AUDITOR.value,
                is_active=True
            ),
        ]
        db.bulk_save_objects(users)
        db.commit()
        print(f"  [+] App users seeded: {len(users)} users.")


def main():
    parser = argparse.ArgumentParser(description="Synthetic Data Seeder")
    parser.add_argument("--scale", type=int, default=10000, help="Number of synthetic employees (default: 10000)")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed random seed (default: 20261022)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        seeder = DatabaseSeeder(seed=args.seed, scale=args.scale)
        seeder.run(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
