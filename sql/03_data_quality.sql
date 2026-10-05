CREATE OR REPLACE TABLE data_quality_results AS
WITH checks AS (
    SELECT
        'dim_hospital_unique_ccn' AS check_name,
        'critical' AS severity,
        COUNT(*) - COUNT(DISTINCT ccn) AS failed_rows,
        'Hospital dimension must contain one row per CCN.' AS detail
    FROM dim_hospital
    UNION ALL
    SELECT
        'valid_six_character_ccn',
        'critical',
        COUNT(*) FILTER (WHERE NOT REGEXP_MATCHES(ccn, '^[0-9]{6}$')),
        'CCN must remain a six-digit text identifier.'
    FROM dim_hospital
    UNION ALL
    SELECT
        'cost_report_unique_ccn',
        'critical',
        COUNT(*) - COUNT(DISTINCT ccn),
        'Latest cost report selection must be unique by CCN.'
    FROM fact_cost_report
    UNION ALL
    SELECT
        'cost_report_financial_reconciliation',
        'warning',
        COUNT(*) FILTER (
            WHERE total_assets IS NOT NULL
              AND total_liabilities_and_fund_balances IS NOT NULL
              AND ABS(total_assets - total_liabilities_and_fund_balances)
                  > GREATEST(1000, ABS(total_assets) * 0.01)
        ),
        'Assets should reconcile to liabilities and fund balances within $1,000 or 1%.'
    FROM fact_cost_report
    UNION ALL
    SELECT
        'nonnegative_beds_and_discharges',
        'critical',
        COUNT(*) FILTER (WHERE number_of_beds < 0 OR total_discharges < 0),
        'Beds and discharges cannot be negative.'
    FROM mart_hospital_benchmark
    UNION ALL
    SELECT
        'overall_rating_domain',
        'critical',
        COUNT(*) FILTER (WHERE overall_rating NOT BETWEEN 1 AND 5),
        'Reported overall ratings must be between one and five stars.'
    FROM mart_hospital_benchmark
    UNION ALL
    SELECT
        'cost_join_coverage',
        'information',
        COUNT(*) FILTER (WHERE fiscal_year_end_date IS NULL),
        'Hospitals without a matched 2023 cost report; this is coverage, not necessarily an error.'
    FROM mart_hospital_benchmark
    UNION ALL
    SELECT
        'quality_join_coverage',
        'information',
        COUNT(*) FILTER (WHERE overall_rating IS NULL),
        'Hospitals without a reported overall rating; CMS suppression and eligibility can apply.'
    FROM mart_hospital_benchmark
)
SELECT
    check_name,
    severity,
    failed_rows,
    CASE WHEN severity = 'critical' AND failed_rows > 0 THEN 'FAIL' ELSE 'PASS' END AS status,
    detail,
    CURRENT_TIMESTAMP AS checked_at_utc
FROM checks;

