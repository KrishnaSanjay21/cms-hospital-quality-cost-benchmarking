"""KPI mart construction and export."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb


def build_kpi_marts(warehouse_path: Path, sql_dir: Path) -> None:
    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute((sql_dir / "02_kpi_marts.sql").read_text(encoding="utf-8"))


def export_marts(warehouse_path: Path, output_dir: Path) -> dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    frames = {}
    with duckdb.connect(str(warehouse_path), read_only=True) as connection:
        for table in ("mart_hospital_benchmark", "mart_state_summary"):
            frame = connection.execute(f"SELECT * FROM {table}").fetch_df()
            frames[table] = frame
            frame.to_parquet(output_dir / f"{table}.parquet", index=False)
            frame.to_csv(output_dir / f"{table}.csv", index=False)
            counts[table] = len(frame)
        quality = connection.execute(
            "SELECT check_name, severity, failed_rows, status, detail FROM data_quality_results"
        ).fetch_df()

    hospital_columns = [
        "ccn",
        "facility_name",
        "city",
        "state",
        "hospital_type",
        "ownership_group",
        "size_band",
        "overall_rating",
        "hcahps_summary_star",
        "mspb_ratio",
        "number_of_beds",
        "total_discharges",
        "bed_occupancy_rate",
        "operating_expense_per_discharge",
        "operating_margin",
        "cost_peer_percentile",
        "quality_peer_percentile",
        "high_cost_peer_flag",
        "low_quality_peer_flag",
        "review_priority_flag",
    ]
    hospitals = frames["mart_hospital_benchmark"].sort_values(
        ["review_priority_flag", "cost_peer_percentile"], ascending=[False, False]
    )

    def records(frame):
        return json.loads(frame.to_json(orient="records", date_format="iso"))

    payload = {
        "hospitals": records(hospitals[hospital_columns]),
        "states": records(frames["mart_state_summary"].sort_values("state")),
        "quality": records(quality),
        "metadata": {
            "publisher": "Centers for Medicare & Medicaid Services",
            "hospital_count": counts["mart_hospital_benchmark"],
            "report_scope": "All hospital-level mart rows, sorted by review priority and cost percentile",
        },
    }
    (output_dir / "report_data.json").write_text(
        json.dumps(payload, indent=2, default=str, allow_nan=False), encoding="utf-8"
    )
    return counts
