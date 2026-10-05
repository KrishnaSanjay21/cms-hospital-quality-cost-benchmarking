from pathlib import Path


def test_kpi_sql_documents_peer_minimum_and_percentiles():
    sql = (Path(__file__).parents[1] / "sql" / "02_kpi_marts.sql").read_text(encoding="utf-8")
    assert "cost_peer_n >= 10" in sql
    assert "PERCENT_RANK()" in sql
    assert "review_priority_flag" in sql


def test_kpi_sql_uses_safe_denominators():
    sql = (Path(__file__).parents[1] / "sql" / "02_kpi_marts.sql").read_text(encoding="utf-8")
    assert sql.count("NULLIF(") >= 7

