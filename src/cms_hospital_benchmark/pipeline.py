"""End-to-end orchestration for the hospital benchmarking warehouse."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .cost_report_api import CostReportClient
from .marts import build_kpi_marts, export_marts
from .normalize import stage_all
from .provider_api import DATASETS, ProviderDataClient
from .quality import run_data_quality
from .settings import Settings
from .warehouse import build_relational_model


def run_pipeline(settings: Settings, project_root: Path, extract: bool = True) -> dict:
    settings.ensure_directories()
    started = datetime.now(timezone.utc)
    manifests: dict[str, dict] = {}

    if extract:
        with ProviderDataClient(
            timeout_seconds=settings.http_timeout_seconds,
            page_size=settings.page_size,
        ) as client:
            for dataset in DATASETS:
                manifests[dataset.name] = client.snapshot(dataset, settings.raw_dir)
        with CostReportClient(
            timeout_seconds=settings.http_timeout_seconds,
            page_size=settings.page_size,
        ) as client:
            manifests["cost_report"] = client.snapshot(settings.raw_dir)

    staged_counts = stage_all(settings.raw_dir, settings.staged_dir)
    sql_dir = project_root / "sql"
    build_relational_model(settings.warehouse_path, settings.staged_dir, sql_dir)
    build_kpi_marts(settings.warehouse_path, sql_dir)
    quality = run_data_quality(settings.warehouse_path, sql_dir)
    mart_counts = export_marts(settings.warehouse_path, settings.data_dir / "exports")

    completed = datetime.now(timezone.utc)
    summary = {
        "status": "success",
        "started_at_utc": started.isoformat(),
        "completed_at_utc": completed.isoformat(),
        "duration_seconds": round((completed - started).total_seconds(), 2),
        "extracted": extract,
        "manifests": manifests,
        "staged_rows": staged_counts,
        "mart_rows": mart_counts,
        "quality_checks": quality.to_dict(orient="records"),
    }
    summary_path = settings.manifest_dir / "latest_run.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary

