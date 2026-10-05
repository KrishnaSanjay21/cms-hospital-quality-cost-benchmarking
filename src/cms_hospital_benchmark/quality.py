"""Warehouse-level data quality checks."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


class DataQualityError(RuntimeError):
    """Raised when one or more critical warehouse checks fail."""


def run_data_quality(warehouse_path: Path, sql_dir: Path) -> pd.DataFrame:
    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute((sql_dir / "03_data_quality.sql").read_text(encoding="utf-8"))
        results = connection.execute(
            "SELECT * FROM data_quality_results ORDER BY severity, check_name"
        ).fetch_df()
    failures = results.query("severity == 'critical' and status == 'FAIL'")
    if not failures.empty:
        names = ", ".join(failures["check_name"].tolist())
        raise DataQualityError(f"Critical data-quality checks failed: {names}")
    return results
