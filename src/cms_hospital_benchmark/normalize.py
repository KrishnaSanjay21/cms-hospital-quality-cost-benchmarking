"""Normalize CMS extracts without changing their analytical grain."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


MISSING_MARKERS = {
    "",
    "Not Available",
    "Not Applicable",
    "Not Available*",
    "N/A",
    "null",
}


def snake_case(value: str) -> str:
    value = value.replace("+", " plus ").replace("%", " percent ").replace("&", " and ")
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return re.sub(r"_+", "_", value)


def normalize_ccn(series: pd.Series) -> pd.Series:
    digits = series.astype("string").str.replace(r"\D", "", regex=True)
    return digits.where(digits.str.len().gt(0)).str.zfill(6)


def numeric(series: pd.Series) -> pd.Series:
    text = series.astype("string").replace(list(MISSING_MARKERS), pd.NA)
    text = text.str.replace(",", "", regex=False).str.replace("$", "", regex=False)
    text = text.str.replace("%", "", regex=False).str.strip()
    return pd.to_numeric(text, errors="coerce")


def normalize_frame(frame: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [snake_case(column) for column in normalized.columns]
    normalized = normalized.replace(list(MISSING_MARKERS), pd.NA)

    ccn_column = "facility_id" if "facility_id" in normalized else "provider_ccn"
    if ccn_column in normalized:
        normalized["ccn"] = normalize_ccn(normalized[ccn_column])

    for column in normalized.columns:
        if column.endswith("_date") or column in {"start_date", "end_date"}:
            normalized[column] = pd.to_datetime(normalized[column], errors="coerce")

    if dataset_name == "hospital_general":
        numeric_columns = [
            column
            for column in normalized.columns
            if column.startswith("count_of_") or column.endswith("_measure_count")
        ] + ["hospital_overall_rating"]
    elif dataset_name in {"hcahps", "complications_deaths", "unplanned_visits", "mspb"}:
        numeric_columns = [
            "score",
            "denominator",
            "lower_estimate",
            "higher_estimate",
            "number_of_patients",
            "number_of_completed_surveys",
            "survey_response_rate_percent",
            "patient_survey_star_rating",
            "hcahps_answer_percent",
            "hcahps_linear_mean_value",
        ]
    else:
        identifiers = {"rpt_rec_num", "provider_ccn", "ccn", "zip_code", "medicare_cbsa_number"}
        numeric_columns = [
            column
            for column in normalized.columns
            if column not in identifiers
            and normalized[column].dtype == "object"
            and column
            not in {
                "hospital_name",
                "street_address",
                "city",
                "state_code",
                "county",
                "rural_versus_urban",
                "ccn_facility_type",
                "provider_type",
                "type_of_control",
                "fiscal_year_begin_date",
                "fiscal_year_end_date",
            }
        ]

    for column in numeric_columns:
        if column in normalized:
            normalized[column] = numeric(normalized[column])

    normalized["source_dataset"] = dataset_name
    return normalized


def stage_all(raw_dir: Path, staged_dir: Path) -> dict[str, int]:
    staged_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for raw_path in sorted(raw_dir.glob("*.parquet")):
        dataset_name = raw_path.stem.replace("hospital_cost_report_2023", "cost_report")
        frame = normalize_frame(pd.read_parquet(raw_path), dataset_name)
        output = staged_dir / f"{dataset_name}.parquet"
        frame.to_parquet(output, index=False)
        counts[dataset_name] = len(frame)
    return counts

