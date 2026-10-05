"""Build the DuckDB relational warehouse from staged Parquet files."""

from __future__ import annotations

from pathlib import Path

import duckdb


STAGED_TABLES = {
    "hospital_general": "stg_hospital_general",
    "hcahps": "stg_hcahps",
    "complications_deaths": "stg_complications_deaths",
    "unplanned_visits": "stg_unplanned_visits",
    "mspb": "stg_mspb",
    "cost_report": "stg_cost_report",
}


def build_relational_model(warehouse_path: Path, staged_dir: Path, sql_dir: Path) -> None:
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(warehouse_path)) as connection:
        for dataset_name, table_name in STAGED_TABLES.items():
            path = (staged_dir / f"{dataset_name}.parquet").resolve().as_posix()
            connection.execute(
                f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet(?)",
                [path],
            )
        connection.execute((sql_dir / "01_relational_model.sql").read_text(encoding="utf-8"))

