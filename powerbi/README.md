# Power BI implementation kit

This folder is a source-controlled implementation kit for a Power BI Desktop report. It does
not claim that a `.pbix` was deployed or that a Power BI Service refresh was configured.

## Build

1. Run `python scripts/run_pipeline.py refresh`.
2. In Power BI Desktop, create a text parameter named `ExportFolder` pointing to
   `<repository>/data/exports`.
3. Paste the two queries in `queries.pq` into Power Query and name them
   `HospitalBenchmark` and `StateSummary`.
4. Mark `ccn` as text. Use `state`, `ownership_group`, `size_band`, and `hospital_type` as
   slicers.
5. Add the measures from `measures.dax` and import `theme.json`.
6. Implement the pages in `dashboard-spec.md` and validate totals against the Excel report.

The two imported marts are already at reporting grain and require no many-to-many relationship.
If a shared geography dimension is added, use one-to-many single-direction relationships.

