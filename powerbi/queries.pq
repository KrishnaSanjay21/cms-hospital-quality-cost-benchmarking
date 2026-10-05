// Query: HospitalBenchmark
let
    Source = Csv.Document(
        File.Contents(ExportFolder & "\\mart_hospital_benchmark.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"ccn", type text}, {"facility_name", type text}, {"state", type text},
        {"overall_rating", type number}, {"hcahps_summary_star", type number},
        {"mspb_ratio", type number}, {"number_of_beds", type number},
        {"operating_expense_per_discharge", Currency.Type},
        {"operating_margin", Percentage.Type}, {"bed_occupancy_rate", Percentage.Type},
        {"high_cost_peer_flag", type logical}, {"low_quality_peer_flag", type logical},
        {"review_priority_flag", type logical}
    })
in
    Typed

// Query: StateSummary
let
    Source = Csv.Document(
        File.Contents(ExportFolder & "\\mart_state_summary.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"state", type text}, {"hospitals", Int64.Type},
        {"median_overall_rating", type number}, {"median_hcahps_star", type number},
        {"median_mspb_ratio", type number},
        {"median_operating_expense_per_discharge", Currency.Type},
        {"review_priority_hospitals", Int64.Type}
    })
in
    Typed

