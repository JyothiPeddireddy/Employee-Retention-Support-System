"""CLI Entrypoint for Synthetic Data Generator.
Usage:
    python -m backend.generator.main --scale 10000 --seed 20261022 --output-dir data/
"""
import argparse
import sys
from backend.services.generator import SyntheticDataGenerator


def main():
    parser = argparse.ArgumentParser(description="Synthetic Longitudinal Workforce Generator")
    parser.add_argument("--scale", type=int, default=10000, help="Number of synthetic employees (default: 10000)")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed random seed (default: 20261022)")
    parser.add_argument("--output-dir", type=str, default="data", help="Output directory for CSVs and JSONs")
    args = parser.parse_args()

    print(f"============================================================")
    print(f"Generating Synthetic Longitudinal Workforce Dataset")
    print(f"Scale: {args.scale} employees | Seed: {args.seed}")
    print(f"Horizon: 24 Months (2024Q1 - 2025Q4) | Target Attrition: 5-15%")
    print(f"============================================================")

    gen = SyntheticDataGenerator(seed=args.seed, scale=args.scale)
    summary = gen.generate_all()

    print(f"[Done] Total Employees Generated: {summary['total_employees']}")
    print(f"[Done] Tenure Snapshots: {summary['total_tenure_snapshots']}")
    print(f"[Done] Workload Snapshots: {summary['total_workload_snapshots']}")
    print(f"[Done] Engagement Surveys: {summary['total_surveys']}")
    print(f"[Done] Promotion Histories: {summary['total_promotions']}")
    print(f"[Done] Future Attrition Outcomes: {summary['total_attrition_outcomes']}")
    print(f"[Done] Injected Anomalies (Ground Truth): {summary['ground_truth_anomalies_count']}")

    print(f"\nExporting artifacts to '{args.output_dir}'...")
    gen.export_to_files(args.output_dir)
    print(f"[Success] All CSV, manifest.json, and ground_truth.json files exported successfully.\n")


if __name__ == "__main__":
    main()
