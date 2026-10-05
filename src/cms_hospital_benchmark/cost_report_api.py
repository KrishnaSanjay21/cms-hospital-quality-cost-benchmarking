"""Client for the CMS data API hospital cost-report product."""

from __future__ import annotations

from pathlib import Path
from typing import Self

import httpx
import pandas as pd
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .io import write_snapshot

COST_REPORT_DATASET_ID = "44060663-47d8-4ced-a115-b53b4c270acb"
COST_API_ROOT = "https://data.cms.gov/data-api/v1/dataset"


class CostReportClient:
    def __init__(self, timeout_seconds: float = 120.0, page_size: int = 5000) -> None:
        self.page_size = page_size
        self.client = httpx.Client(timeout=timeout_seconds, follow_redirects=True)

    @property
    def source_url(self) -> str:
        return f"{COST_API_ROOT}/{COST_REPORT_DATASET_ID}/data"

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _page(self, offset: int) -> list[dict]:
        response = self.client.get(
            self.source_url,
            params={"size": self.page_size, "offset": offset},
        )
        response.raise_for_status()
        return response.json()

    def fetch(self) -> pd.DataFrame:
        rows: list[dict] = []
        offset = 0
        while True:
            page_rows = self._page(offset)
            rows.extend(page_rows)
            if len(page_rows) < self.page_size:
                break
            offset += len(page_rows)
        return pd.DataFrame(rows)

    def snapshot(self, raw_dir: Path) -> dict:
        return write_snapshot(
            self.fetch(),
            raw_dir / "hospital_cost_report_2023.parquet",
            self.source_url,
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
