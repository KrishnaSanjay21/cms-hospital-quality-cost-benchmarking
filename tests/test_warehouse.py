from pathlib import Path

import duckdb
import pandas as pd

from cms_hospital_benchmark.warehouse import STAGED_TABLES


def test_every_expected_staging_table_has_a_dataset_name():
    assert set(STAGED_TABLES) == {
        "hospital_general",
        "hcahps",
        "complications_deaths",
        "unplanned_visits",
        "mspb",
        "cost_report",
    }


def test_duckdb_preserves_six_character_ccn(tmp_path: Path):
    parquet_path = tmp_path / "hospital.parquet"
    pd.DataFrame({"ccn": ["010001"]}).to_parquet(parquet_path, index=False)
    with duckdb.connect() as connection:
        value = connection.execute("SELECT ccn FROM read_parquet(?)", [str(parquet_path)]).fetchone()[0]
    assert value == "010001"

