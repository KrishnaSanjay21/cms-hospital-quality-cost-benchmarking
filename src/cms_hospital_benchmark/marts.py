"""KPI mart construction and export."""

from __future__ import annotations

from pathlib import Path

import duckdb


def build_kpi_marts(warehouse_path: Path, sql_dir: Path) -> None:
    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute((sql_dir / "02_kpi_marts.sql").read_text(encoding="utf-8"))


def export_marts(warehouse_path: Path, output_dir: Path) -> dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    with duckdb.connect(str(warehouse_path), read_only=True) as connection:
        for table in ("mart_hospital_benchmark", "mart_state_summary"):
            frame = connection.execute(f"SELECT * FROM {table}").fetch_df()
            frame.to_parquet(output_dir / f"{table}.parquet", index=False)
            frame.to_csv(output_dir / f"{table}.csv", index=False)
            counts[table] = len(frame)
    return counts

