import pandas as pd

from cms_hospital_benchmark.normalize import normalize_ccn, normalize_frame, snake_case


def test_snake_case_handles_financial_labels():
    assert snake_case("Combined Outpatient + Inpatient Total Charges") == (
        "combined_outpatient_plus_inpatient_total_charges"
    )


def test_ccn_retains_leading_zeroes():
    result = normalize_ccn(pd.Series(["1001", "010005"]))
    assert result.tolist() == ["001001", "010005"]


def test_provider_missing_markers_and_rating_become_numeric():
    frame = pd.DataFrame(
        {
            "Facility ID": ["010001", "010002"],
            "Hospital overall rating": ["4", "Not Available"],
        }
    )
    result = normalize_frame(frame, "hospital_general")
    assert result.loc[0, "hospital_overall_rating"] == 4
    assert pd.isna(result.loc[1, "hospital_overall_rating"])

