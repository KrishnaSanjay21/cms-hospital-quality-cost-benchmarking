# KPI dictionary

| KPI | Formula / source | Unit | Interpretation limit |
|---|---|---:|---|
| Overall rating | CMS Hospital General Information | 1–5 stars | CMS eligibility/suppression applies; period may differ from cost report. |
| HCAHPS summary star | HCAHPS `H_STAR_RATING` | 1–5 stars | Patient-experience measure, not a clinical outcome. |
| Top-box hospital rating | HCAHPS `H_HSP_RATING_9_10` | % | Share responding 9 or 10; survey denominator retained. |
| Definitely recommend | HCAHPS `H_RECMND_DY` | % | Survey top-box result; survey denominator retained. |
| Worse outcome measures | Count of measures labeled worse than national | measures | Count depends on measures reported and CMS comparison methods. |
| MSPB ratio | CMS Medicare Spending per Beneficiary score | ratio | Episode spending relative to national median; not total hospital cost. |
| Bed occupancy proxy | Total inpatient days ÷ available bed days | % | Uses cost-report values and is not a real-time staffed-bed occupancy rate. |
| Discharges per bed | Total discharges ÷ number of beds | discharges/bed | Fiscal-period utilization context. |
| Expense per discharge | Total operating expense ÷ total discharges | USD/discharge | Accounting benchmark; case mix is not risk adjusted here. |
| Operating margin proxy | Net income from service to patients ÷ net patient revenue | % | Based on submitted cost-report fields. |
| Liabilities to assets | Total liabilities ÷ total assets | ratio | Balance-sheet leverage indicator, not a credit rating. |
| High-cost peer flag | Expense/discharge at or above peer 90th percentile | Boolean | Only assigned with at least 10 non-null peers. |
| Low-quality peer flag | Overall rating at or below peer 10th percentile | Boolean | Descriptive screen, not a claim of poor care. |
| Review priority flag | Both high-cost and low-quality peer flags | Boolean | Triage signal for review; no causal interpretation. |

Peer groups combine CMS hospital type and a transparent bed-size band: small under 100,
medium 100–299, and large 300 or more. Missing bed counts are labeled unknown.

