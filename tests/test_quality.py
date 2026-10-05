from pathlib import Path


def test_quality_sql_has_critical_and_informational_checks():
    sql = (Path(__file__).parents[1] / "sql" / "03_data_quality.sql").read_text(encoding="utf-8")
    assert "'critical'" in sql
    assert "'information'" in sql
    assert "cost_report_financial_reconciliation" in sql


def test_coverage_is_not_mislabeled_as_failure():
    sql = (Path(__file__).parents[1] / "sql" / "03_data_quality.sql").read_text(encoding="utf-8")
    assert "CMS suppression and eligibility can apply" in sql

