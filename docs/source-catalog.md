# Source catalog

| Domain | Official CMS product | Join key | Grain retained |
|---|---|---|---|
| Provider attributes | [Hospital General Information](https://data.cms.gov/provider-data/dataset/xubh-q36u) | Facility ID / CCN | Hospital |
| Patient experience | [HCAHPS](https://data.cms.gov/provider-data/dataset/dgck-syfz) | Facility ID / CCN | Hospital × HCAHPS measure |
| Clinical outcomes | [Complications and Deaths](https://data.cms.gov/provider-data/dataset/ynj2-r877) | Facility ID / CCN | Hospital × outcome measure |
| Utilization outcomes | [Unplanned Hospital Visits](https://data.cms.gov/provider-data/dataset/632h-zaca) | Facility ID / CCN | Hospital × visit measure |
| Episode spending | [Medicare Spending per Beneficiary](https://data.cms.gov/provider-data/dataset/rrqw-56er) | Facility ID / CCN | Hospital × MSPB measure |
| Financial/utilization | [2023 Hospital Cost Report](https://data.cms.gov/provider-compliance/cost-reports/hospital-provider-cost-report) | Provider CCN | Cost-report filing |

All joins preserve the six-character CMS Certification Number as text so leading zeroes are
not lost. The analytical model also retains measure and fiscal-period dates. National and
state aggregate rows are not substituted for hospital observations.

## Interpretation boundary

CMS sources use different collection periods, populations, risk adjustments, and suppressions.
The warehouse therefore exposes domain-specific KPIs and flags instead of inventing a universal
hospital score. Comparisons are descriptive and intended for portfolio demonstration.

