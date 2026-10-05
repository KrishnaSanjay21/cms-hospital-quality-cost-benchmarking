"""Client for the CMS Provider Data API."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Self

import httpx
import pandas as pd
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .io import write_snapshot

PROVIDER_API_ROOT = "https://data.cms.gov/provider-data/api/1/datastore/query"


@dataclass(frozen=True)
class ProviderDataset:
    name: str
    dataset_id: str


DATASETS = (
    ProviderDataset("hospital_general", "xubh-q36u"),
    ProviderDataset("hcahps", "dgck-syfz"),
    ProviderDataset("complications_deaths", "ynj2-r877"),
    ProviderDataset("unplanned_visits", "632h-zaca"),
    ProviderDataset("mspb", "rrqw-56er"),
)


class ProviderDataClient:
    def __init__(self, timeout_seconds: float = 120.0, page_size: int = 5000) -> None:
        self.page_size = page_size
        self.client = httpx.Client(timeout=timeout_seconds, follow_redirects=True)

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _page(self, dataset_id: str, offset: int) -> dict:
        url = f"{PROVIDER_API_ROOT}/{dataset_id}/0"
        response = self.client.get(url, params={"limit": self.page_size, "offset": offset})
        response.raise_for_status()
        return response.json()

    def fetch(self, dataset_id: str) -> pd.DataFrame:
        rows: list[dict] = []
        offset = 0
        expected_count: int | None = None
        while expected_count is None or offset < expected_count:
            payload = self._page(dataset_id, offset)
            page_rows = payload.get("results", [])
            expected_count = int(payload.get("count", len(page_rows)))
            rows.extend(page_rows)
            if not page_rows:
                break
            offset += len(page_rows)
        if expected_count is not None and len(rows) != expected_count:
            raise ValueError(
                f"Incomplete CMS extract for {dataset_id}: {len(rows)} of {expected_count}"
            )
        return pd.DataFrame(rows)

    def snapshot(self, dataset: ProviderDataset, raw_dir: Path) -> dict:
        frame = self.fetch(dataset.dataset_id)
        source_url = f"{PROVIDER_API_ROOT}/{dataset.dataset_id}/0"
        return write_snapshot(frame, raw_dir / f"{dataset.name}.parquet", source_url)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
