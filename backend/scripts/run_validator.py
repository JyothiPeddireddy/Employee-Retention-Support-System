"""CLI Entrypoint for Data Validator & Anomaly Audit.
Usage:
    python -m backend.validator.main --data-dir data/
"""
import argparse
import os
import csv
import json
from backend.app.services.validator import DataValidator


def load_dataset_from_csv(data_dir: str):
    """Load exported CSVs and ground_truth.json into data dictionary for validation."""
    tables = [
        "teams", "compensation_bands", "roles", "employees",
        "tenure_snapshots", "workload_snapshots", "engagement_surveys",
        "promotion_histories", "attrition_outcomes", "interventions",
        "ground_truth_anomalies"
    ]
    data_store = {}

    for t in tables:
        csv_file = os.path.join(data_dir, f"{t}.csv")
        if not os.path.exists(csv_file):
            for sub in ["generated", "ground_truth", "exports"]:
                sub_path = os.path.join(data_dir, sub, f"{t}.csv")
                if os.path.exists(sub_path):
                    csv_file = sub_path
                    break

        rows = []
        if os.path.exists(csv_file):
            with open(csv_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    # Parse numeric types
                    converted = {}
                    for k, v in r.items():
                        if v == "" or v is None:
                            converted[k] = None
                        elif k in ["min_salary", "mid_salary", "max_salary", "current_salary", "from_salary", "to_salary", "avg_weekly_hours", "overtime_hours", "satisfaction_score", "work_life_balance_score", "career_growth_score", "manager_support_score", "composite_engagement"]:
                            converted[k] = float(v)
                        elif k in ["tenure_months", "months_in_current_role", "consecutive_overtime_weeks", "active_project_count"]:
                            converted[k] = int(v)
                        elif k in ["is_missing", "is_benign_surge", "voluntary"]:
                            converted[k] = (v.lower() == "true")
                        else:
                            converted[k] = v
                    rows.append(converted)
        data_store[t] = rows

    return data_store


def main():
    parser = argparse.ArgumentParser(description="Data Validator and Compliance Suite")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory containing CSV files and ground_truth.json")
    args = parser.parse_args()

    print(f"============================================================")
    print(f"Running Data Quality, Temporal Boundary & Anomaly Validation")
    print(f"Target Directory: '{args.data_dir}'")
    print(f"============================================================")

    data_store = load_dataset_from_csv(args.data_dir)
    if not data_store.get("employees"):
        print(f"[Error] No employee data found in '{args.data_dir}'. Run generator first!")
        return

    validator = DataValidator(data_store)
    report = validator.run_all_validations()

    print(f"\n[Validation Summary]")
    print(f"Total Checks:  {report.total_checks}")
    print(f"Passed Checks: {report.passed_checks}")
    print(f"Failed Checks: {report.failed_checks}")
    print(f"Status:        {report.integrity_status}")

    print(f"\n[Detailed Check Results]")
    for c in report.check_results:
        mark = "[PASS]" if c.passed else "[FAIL]"
        print(f"  {mark} {c.check_name:<40} (Checked: {c.total_records_checked}, Failed: {c.failed_count})")
        if c.anomaly_type_detected:
            print(f"         Detected Expected Anomaly: {c.anomaly_type_detected}")

    print(f"\n[Ground Truth Reconciliation]")
    for k, v in report.ground_truth_reconciliation.items():
        print(f"  {k}: {v}")

    # Export report
    report_dir = os.path.join(args.data_dir, "exports") if os.path.isdir(os.path.join(args.data_dir, "exports")) else args.data_dir
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    print(f"\n[Success] Validation report saved to '{report_path}'.\n")


if __name__ == "__main__":
    main()
