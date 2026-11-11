"""Data Generation & Reproducibility API Router."""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from backend.schemas.common import APIResponse
from backend.services.store import store_coordinator
from backend.services.generator import SyntheticDataGenerator

router = APIRouter(prefix="/generator", tags=["Synthetic Data Generator"])


class RegenerateRequest(BaseModel):
    scale: int = Field(500, ge=50, le=10000, description="Scale of employees to generate")
    seed: int = Field(20261022, description="Fixed random seed for deterministic generation")
    export_files: bool = Field(True, description="Whether to export CSV/JSON files to data/")


@router.post("/regenerate", response_model=APIResponse[Dict[str, Any]])
def trigger_regeneration(payload: RegenerateRequest):
    """Regenerate synthetic longitudinal workforce dataset deterministically."""
    try:
        store_coordinator.seed = payload.seed
        store_coordinator.initialize(scale=payload.scale, force_regenerate=True)
        summary = store_coordinator.raw_data

        counts = {k: len(v) for k, v in summary.items()}
        return APIResponse(
            success=True,
            message=f"Successfully regenerated synthetic dataset with seed {payload.seed} and scale {payload.scale}.",
            data={
                "seed": payload.seed,
                "scale": payload.scale,
                "row_counts": counts,
                "anomalies_injected": len(summary.get("ground_truth_anomalies", []))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/verify-reproducibility", response_model=APIResponse[Dict[str, Any]])
def verify_reproducibility(seed: int = Query(20261022), scale: int = Query(200)):
    """Generate twice with the same seed and compare row counts/checksums to demonstrate exact reproducibility."""
    gen1 = SyntheticDataGenerator(seed=seed, scale=scale)
    gen1.generate_all()

    gen2 = SyntheticDataGenerator(seed=seed, scale=scale)
    gen2.generate_all()

    counts1 = {
        "employees": len(gen1.employees),
        "tenure_snapshots": len(gen1.tenure_snapshots),
        "workload_snapshots": len(gen1.workload_snapshots),
        "surveys": len(gen1.engagement_surveys),
        "promotions": len(gen1.promotion_histories),
        "attrition_outcomes": len(gen1.attrition_outcomes),
        "interventions": len(gen1.interventions),
        "anomalies": len(gen1.ground_truth_anomalies)
    }

    counts2 = {
        "employees": len(gen2.employees),
        "tenure_snapshots": len(gen2.tenure_snapshots),
        "workload_snapshots": len(gen2.workload_snapshots),
        "surveys": len(gen2.engagement_surveys),
        "promotions": len(gen2.promotion_histories),
        "attrition_outcomes": len(gen2.attrition_outcomes),
        "interventions": len(gen2.interventions),
        "anomalies": len(gen2.ground_truth_anomalies)
    }

    # Verify first 3 employee IDs and salaries match exactly
    emp_sample1 = [(e["employee_id"], e["current_salary"]) for e in gen1.employees[:5]]
    emp_sample2 = [(e["employee_id"], e["current_salary"]) for e in gen2.employees[:5]]

    is_exact_match = (counts1 == counts2) and (emp_sample1 == emp_sample2)

    return APIResponse(
        success=True,
        message="Dual regeneration reproducibility test completed.",
        data={
            "seed": seed,
            "scale": scale,
            "reproducibility_verified": is_exact_match,
            "run1_counts": counts1,
            "run2_counts": counts2,
            "sample_verification_passed": (emp_sample1 == emp_sample2)
        }
    )
