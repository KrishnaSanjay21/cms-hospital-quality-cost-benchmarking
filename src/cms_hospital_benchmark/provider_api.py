"""Client for the CMS Provider Data API."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Self

import httpx
import pandas as pd
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .io import write_snapshot

PROVIDER_API_ROOT = "https://data.cms.gov/provider-data/api/1/datastore/query"
PROVIDER_METADATA_ROOT = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items"


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
    def __init__(self, timeout_seconds: float = 120.0, page_size: int = 1000) -> None:
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

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def fetch_download(self, dataset_id: str) -> tuple[pd.DataFrame, str]:
        metadata_response = self.client.get(f"{PROVIDER_METADATA_ROOT}/{dataset_id}")
        metadata_response.raise_for_status()
        distributions = metadata_response.json().get("distribution", [])
        csv_distribution = next(
            item for item in distributions if item.get("mediaType") == "text/csv"
        )
        download_url = csv_distribution["downloadURL"]
        response = self.client.get(download_url)
        response.raise_for_status()
        frame = pd.read_csv(BytesIO(response.content), dtype="string", low_memory=False)
        return frame, download_url

    def snapshot(self, dataset: ProviderDataset, raw_dir: Path) -> dict:
        frame, source_url = self.fetch_download(dataset.dataset_id)
        return write_snapshot(frame, raw_dir / f"{dataset.name}.parquet", source_url)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
