# Operations runbook

## Full refresh

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python scripts/run_pipeline.py refresh
pytest
```

Use `refresh --skip-extract` to rebuild from already downloaded raw snapshots. A successful run
writes `data/manifests/latest_run.json`, reporting marts under `data/exports`, and the local
DuckDB database under `warehouse/`.

## Troubleshooting

- **HTTP 429/5xx:** the clients retry transient HTTP errors four times with exponential backoff.
  Re-run later if CMS remains unavailable.
- **Incomplete provider extract:** pagination validates returned rows against the API count and
  stops with an error rather than silently loading a partial dataset.
- **Critical DQ failure:** inspect `data_quality_results` in DuckDB. Do not publish refreshed
  outputs until identifier, uniqueness, domain, or negative-value failures are resolved.
- **Lower match coverage:** inspect facility IDs and source periods first. Missing rows can be
  valid because products have different eligibility and release schedules.
- **Power BI mismatch:** confirm `ccn` is text and reconcile totals against the CSV export and
  Excel report before modifying transformations.

## Release checklist

1. Confirm every raw snapshot has a checksum manifest.
2. Confirm all critical data-quality checks pass.
3. Review measure periods and join coverage.
4. Rebuild and visually inspect the Excel report.
5. Reconcile Power BI cards to the state and hospital mart exports.
6. Record the CMS retrieval timestamp in release notes.

