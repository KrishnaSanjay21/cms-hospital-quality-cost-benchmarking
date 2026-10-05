# Executive dashboard specification

## Page 1 — Executive benchmark

- KPI cards: hospital count, median overall rating, median MSPB ratio, median expense per
  discharge, review-priority hospitals, rating coverage.
- State map: median expense per discharge; tooltip shows rating, HCAHPS, MSPB, and coverage.
- Scatter: expense per discharge vs. overall rating; size = beds; color = priority flag.
- Ranked table: facility, state, ownership, size, rating, HCAHPS, MSPB, expense/discharge,
  operating margin, peer flags.
- Slicers: state, ownership group, size band, hospital type, urban/rural.

## Page 2 — Quality and experience

- Distribution of overall ratings by hospital type and ownership.
- HCAHPS summary star and “definitely recommend” percentage by state.
- Worse-than-national outcome-measure counts; retain measure coverage in the tooltip.

## Page 3 — Cost and utilization

- Expense per discharge, bed occupancy proxy, discharges per bed, MSPB ratio, and operating
  margin by peer group.
- Cost-report fiscal year end displayed in the subtitle/tooltip.

## Page 4 — Review queue and definitions

- Drill-through table restricted to high-cost, low-quality, or combined priority flags.
- Text cards define 90th/10th percentile rules and minimum peer size of 10.
- Coverage matrix and link to the KPI dictionary.

## Accessibility and validation

- Do not encode status by color alone; use text flags and icons.
- Add alt text to every chart and tab order to each page.
- Reconcile hospital counts and medians to `cms_hospital_comparison.xlsx` before sharing.

