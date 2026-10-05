CREATE OR REPLACE TEMP TABLE experience_rollup AS
SELECT
    ccn,
    MAX(CASE WHEN measure_id = 'H_STAR_RATING' THEN patient_survey_star_rating END) AS hcahps_summary_star,
    MAX(CASE WHEN measure_id = 'H_HSP_RATING_9_10' THEN hcahps_answer_percent END) AS top_box_hospital_rating_pct,
    MAX(CASE WHEN measure_id = 'H_RECMND_DY' THEN hcahps_answer_percent END) AS definitely_recommend_pct,
    MAX(number_of_completed_surveys) AS hcahps_completed_surveys,
    MAX(period_end) AS hcahps_period_end
FROM fact_patient_experience
GROUP BY ccn;

CREATE OR REPLACE TEMP TABLE outcome_rollup AS
SELECT
    ccn,
    COUNT(*) FILTER (WHERE LOWER(COALESCE(compared_to_national, '')) LIKE '%worse%') AS worse_outcome_measure_count,
    COUNT(*) FILTER (WHERE LOWER(COALESCE(compared_to_national, '')) LIKE '%better%') AS better_outcome_measure_count,
    COUNT(*) FILTER (WHERE score IS NOT NULL) AS reported_outcome_measure_count,
    MAX(period_end) AS outcome_period_end
FROM fact_outcome
GROUP BY ccn;

CREATE OR REPLACE TEMP TABLE mspb_rollup AS
SELECT ccn, MAX(mspb_ratio) AS mspb_ratio, MAX(period_end) AS mspb_period_end
FROM fact_mspb
GROUP BY ccn;

CREATE OR REPLACE TEMP TABLE benchmark_base AS
SELECT
    h.ccn,
    h.facility_name,
    h.city,
    h.state,
    h.county,
    h.hospital_type,
    h.hospital_ownership,
    CASE
        WHEN LOWER(h.hospital_ownership) LIKE '%voluntary non-profit%' THEN 'Voluntary non-profit'
        WHEN LOWER(h.hospital_ownership) LIKE '%proprietary%' THEN 'Proprietary'
        WHEN LOWER(h.hospital_ownership) LIKE '%government%' THEN 'Government'
        ELSE 'Other / unknown'
    END AS ownership_group,
    h.emergency_services,
    h.hospital_overall_rating AS overall_rating,
    COALESCE(h.count_of_mort_measures_worse, 0)
      + COALESCE(h.count_of_safety_measures_worse, 0)
      + COALESCE(h.count_of_readm_measures_worse, 0) AS general_info_worse_measure_count,
    e.hcahps_summary_star,
    e.top_box_hospital_rating_pct,
    e.definitely_recommend_pct,
    e.hcahps_completed_surveys,
    e.hcahps_period_end,
    o.worse_outcome_measure_count,
    o.better_outcome_measure_count,
    o.reported_outcome_measure_count,
    o.outcome_period_end,
    m.mspb_ratio,
    m.mspb_period_end,
    c.rural_versus_urban,
    c.ccn_facility_type,
    c.type_of_control,
    c.fiscal_year_end_date,
    c.number_of_beds,
    CASE
        WHEN c.number_of_beds IS NULL THEN 'Unknown'
        WHEN c.number_of_beds < 100 THEN 'Small (<100 beds)'
        WHEN c.number_of_beds < 300 THEN 'Medium (100-299 beds)'
        ELSE 'Large (300+ beds)'
    END AS size_band,
    c.fte_employees_on_payroll,
    c.total_bed_days_available,
    c.total_days_v_plus_xviii_plus_xix_plus_unknown AS total_inpatient_days,
    c.total_discharges_v_plus_xviii_plus_xix_plus_unknown AS total_discharges,
    c.total_costs,
    c.total_assets,
    c.total_liabilities,
    c.total_patient_revenue,
    c.net_patient_revenue,
    c.less_total_operating_expense AS operating_expense,
    c.net_income_from_service_to_patients,
    c.total_income,
    c.net_income,
    c.cost_to_charge_ratio,
    c.total_days_v_plus_xviii_plus_xix_plus_unknown
      / NULLIF(c.total_bed_days_available, 0) AS bed_occupancy_rate,
    c.total_discharges_v_plus_xviii_plus_xix_plus_unknown
      / NULLIF(c.number_of_beds, 0) AS discharges_per_bed,
    c.fte_employees_on_payroll / NULLIF(c.number_of_beds, 0) AS fte_per_bed,
    c.less_total_operating_expense
      / NULLIF(c.total_discharges_v_plus_xviii_plus_xix_plus_unknown, 0) AS operating_expense_per_discharge,
    c.net_patient_revenue
      / NULLIF(c.total_discharges_v_plus_xviii_plus_xix_plus_unknown, 0) AS net_patient_revenue_per_discharge,
    c.net_income_from_service_to_patients
      / NULLIF(c.net_patient_revenue, 0) AS operating_margin,
    c.net_income / NULLIF(c.total_income, 0) AS total_margin,
    c.total_liabilities / NULLIF(c.total_assets, 0) AS liabilities_to_assets
FROM dim_hospital h
LEFT JOIN experience_rollup e USING (ccn)
LEFT JOIN outcome_rollup o USING (ccn)
LEFT JOIN mspb_rollup m USING (ccn)
LEFT JOIN fact_cost_report c USING (ccn);

CREATE OR REPLACE TEMP TABLE benchmark_ranked AS
SELECT
    *,
    hospital_type || ' | ' || size_band AS peer_group,
    COUNT(operating_expense_per_discharge) OVER (
        PARTITION BY hospital_type, size_band
    ) AS cost_peer_n,
    PERCENT_RANK() OVER (
        PARTITION BY hospital_type, size_band
        ORDER BY operating_expense_per_discharge
    ) AS cost_peer_percentile,
    COUNT(overall_rating) OVER (
        PARTITION BY hospital_type, size_band
    ) AS quality_peer_n,
    PERCENT_RANK() OVER (
        PARTITION BY hospital_type, size_band
        ORDER BY overall_rating
    ) AS quality_peer_percentile
FROM benchmark_base;

CREATE OR REPLACE TABLE mart_hospital_benchmark AS
SELECT
    *,
    CASE
        WHEN cost_peer_n >= 10 AND cost_peer_percentile >= 0.90 THEN TRUE
        ELSE FALSE
    END AS high_cost_peer_flag,
    CASE
        WHEN quality_peer_n >= 10 AND quality_peer_percentile <= 0.10 THEN TRUE
        ELSE FALSE
    END AS low_quality_peer_flag,
    CASE
        WHEN cost_peer_n >= 10 AND cost_peer_percentile >= 0.90
         AND quality_peer_n >= 10 AND quality_peer_percentile <= 0.10 THEN TRUE
        ELSE FALSE
    END AS review_priority_flag
FROM benchmark_ranked;

CREATE OR REPLACE TABLE mart_state_summary AS
SELECT
    state,
    COUNT(*) AS hospitals,
    COUNT(overall_rating) AS hospitals_with_rating,
    MEDIAN(overall_rating) AS median_overall_rating,
    MEDIAN(hcahps_summary_star) AS median_hcahps_star,
    MEDIAN(mspb_ratio) AS median_mspb_ratio,
    MEDIAN(operating_expense_per_discharge) AS median_operating_expense_per_discharge,
    AVG(CASE WHEN high_cost_peer_flag THEN 1.0 ELSE 0.0 END) AS high_cost_flag_rate,
    AVG(CASE WHEN low_quality_peer_flag THEN 1.0 ELSE 0.0 END) AS low_quality_flag_rate,
    SUM(CASE WHEN review_priority_flag THEN 1 ELSE 0 END) AS review_priority_hospitals
FROM mart_hospital_benchmark
GROUP BY state;

