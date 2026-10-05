CREATE OR REPLACE TABLE dim_hospital AS
SELECT
    ccn,
    facility_name,
    address,
    citytown AS city,
    state,
    zip_code,
    countyparish AS county,
    hospital_type,
    hospital_ownership,
    emergency_services,
    hospital_overall_rating,
    count_of_mort_measures_worse,
    count_of_safety_measures_worse,
    count_of_readm_measures_worse
FROM stg_hospital_general
WHERE ccn IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY ccn ORDER BY facility_name) = 1;

CREATE OR REPLACE TABLE fact_patient_experience AS
SELECT
    ccn,
    hcahps_measure_id AS measure_id,
    hcahps_question AS measure_name,
    patient_survey_star_rating,
    hcahps_answer_percent,
    hcahps_linear_mean_value,
    number_of_completed_surveys,
    survey_response_rate_percent,
    start_date AS period_start,
    end_date AS period_end
FROM stg_hcahps
WHERE ccn IS NOT NULL;

CREATE OR REPLACE TABLE fact_outcome AS
SELECT
    ccn,
    'complications_deaths' AS outcome_domain,
    measure_id,
    measure_name,
    compared_to_national,
    denominator,
    score,
    lower_estimate,
    higher_estimate,
    start_date AS period_start,
    end_date AS period_end
FROM stg_complications_deaths
WHERE ccn IS NOT NULL
UNION ALL
SELECT
    ccn,
    'unplanned_visits' AS outcome_domain,
    measure_id,
    measure_name,
    compared_to_national,
    denominator,
    score,
    lower_estimate,
    higher_estimate,
    start_date AS period_start,
    end_date AS period_end
FROM stg_unplanned_visits
WHERE ccn IS NOT NULL;

CREATE OR REPLACE TABLE fact_mspb AS
SELECT
    ccn,
    measure_id,
    score AS mspb_ratio,
    start_date AS period_start,
    end_date AS period_end
FROM stg_mspb
WHERE ccn IS NOT NULL;

CREATE OR REPLACE TABLE fact_cost_report AS
SELECT
    ccn,
    rpt_rec_num,
    hospital_name,
    state_code,
    ccn_facility_type,
    provider_type,
    type_of_control,
    rural_versus_urban,
    fiscal_year_begin_date,
    fiscal_year_end_date,
    fte_employees_on_payroll,
    number_of_beds,
    total_bed_days_available,
    total_days_v_plus_xviii_plus_xix_plus_unknown,
    total_discharges_v_plus_xviii_plus_xix_plus_unknown,
    total_costs,
    total_assets,
    total_liabilities,
    total_fund_balances,
    total_liabilities_and_fund_balances,
    inpatient_revenue,
    outpatient_revenue,
    total_patient_revenue,
    net_patient_revenue,
    less_total_operating_expense,
    net_income_from_service_to_patients,
    total_income,
    net_income,
    cost_to_charge_ratio
FROM stg_cost_report
WHERE ccn IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY ccn
    ORDER BY fiscal_year_end_date DESC NULLS LAST, TRY_CAST(rpt_rec_num AS BIGINT) DESC NULLS LAST
) = 1;

