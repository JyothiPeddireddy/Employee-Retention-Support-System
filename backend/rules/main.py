"""CLI Entrypoint for Rules & Explainable Prioritization Engine.
Usage:
    python -m backend.rules.main --data-dir data/ --top 10
"""
import argparse
import os
import sys
from backend.validator.main import load_dataset_from_csv
from backend.services.rules import PrioritizationRulesEngine


def main():
    parser = argparse.ArgumentParser(description="Explainable Retention Rules Engine")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory containing CSV files")
    parser.add_argument("--top", type=int, default=10, help="Number of top prioritized employees to show")
    parser.add_argument("--department", type=str, default=None, help="Filter by department")
    args = parser.parse_args()

    print(f"============================================================")
    print(f"Evaluating Supportive Retention Signals (Explainable Rules)")
    print(f"Target Directory: '{args.data_dir}'")
    print(f"============================================================")

    data_store = load_dataset_from_csv(args.data_dir)
    if not data_store.get("employees"):
        print(f"[Error] No employee data found in '{args.data_dir}'. Run generator first!")
        return

    engine = PrioritizationRulesEngine(data_store)
    prioritized = engine.evaluate_all(department_filter=args.department)

    summary = engine.get_summary(prioritized)
    print(f"\n[Prioritization Summary]")
    print(f"Total Active Evaluated: {summary.total_evaluated}")
    print(f"High Priority Candidates: {summary.high_priority_count}")
    print(f"Medium Priority Candidates: {summary.medium_priority_count}")
    print(f"Low Priority Candidates: {summary.low_priority_count}")

    print(f"\nTop {args.top} Employees Prioritized for Supportive Check-ins:")
    print("-" * 80)
    for idx, p in enumerate(prioritized[:args.top], 1):
        print(f"{idx}. [{p.priority_tier}] {p.full_name} ({p.employee_id}) - Score: {p.composite_priority_score}/100")
        print(f"   Role: {p.role_title} ({p.role_level}) | Team: {p.team_name} ({p.department})")
        print(f"   Tenure: {p.tenure_months} mos total ({p.months_in_role} mos in role)")
        print(f"   Key Factors:")
        for f in p.factors:
            print(f"     • [{f.category}] {f.signal_name}: {f.raw_value}")
            print(f"       Guidance: {f.supportive_guidance}")
        print(f"   Recommended 1-on-1 Topics: {', '.join(p.recommended_topics)}")
        print("-" * 80)


if __name__ == "__main__":
    main()
