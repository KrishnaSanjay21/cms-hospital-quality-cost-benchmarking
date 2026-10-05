import fs from "node:fs/promises";

const artifactToolPath = process.env.ARTIFACT_TOOL_PATH || "@oai/artifact-tool";
const { SpreadsheetFile, Workbook } = await import(artifactToolPath);

const root = new URL("..", import.meta.url).pathname.replace(/^\/(?:([A-Za-z]:))/, "$1");
const payload = JSON.parse(await fs.readFile(`${root}/data/exports/report_data.json`, "utf8"));
const outputDir = `${root}/outputs/cms-hospital-quality-cost-benchmarking`;
const previewDir = `${root}/data/report_previews`;

const wb = Workbook.create();
const summary = wb.worksheets.add("Executive Summary");
const hospitals = wb.worksheets.add("Hospital Comparison");
const states = wb.worksheets.add("State Benchmarks");
const quality = wb.worksheets.add("Data Quality");
const definitions = wb.worksheets.add("KPI Definitions");

const navy = "#123047";
const blue = "#2374AB";
const teal = "#2A9D8F";
const paleBlue = "#EAF3F8";
const paleGray = "#F3F5F7";
const amber = "#FFF3CD";
const red = "#F8D7DA";
const font = "Arial";

for (const sheet of [summary, hospitals, states, quality, definitions]) {
  sheet.showGridLines = false;
}
summary.tabColor = navy;
hospitals.tabColor = blue;
states.tabColor = teal;
quality.tabColor = "#F4A261";
definitions.tabColor = "#7A8791";

const hospitalEnd = payload.hospitals.length + 1;
const hospitalHeaders = [
  "CCN", "Facility", "City", "State", "Hospital type", "Ownership group", "Size band",
  "Overall rating", "HCAHPS star", "MSPB ratio", "Beds", "Discharges", "Bed occupancy proxy",
  "Operating expense / discharge", "Operating margin proxy", "Cost peer percentile",
  "Quality peer percentile", "High-cost flag", "Low-quality flag", "Priority flag", "Review category",
];
hospitals.getRange("A1:U1").values = [hospitalHeaders];
hospitals.getRange(`A2:U${hospitalEnd}`).values = payload.hospitals.map((row) => [
  row.ccn, row.facility_name, row.city, row.state, row.hospital_type, row.ownership_group,
  row.size_band, row.overall_rating, row.hcahps_summary_star, row.mspb_ratio, row.number_of_beds,
  row.total_discharges, row.bed_occupancy_rate, row.operating_expense_per_discharge,
  row.operating_margin, row.cost_peer_percentile, row.quality_peer_percentile,
  row.high_cost_peer_flag, row.low_quality_peer_flag, row.review_priority_flag, null,
]);
hospitals.getRange("U2").formulas = [[
  '=IF(T2=TRUE,"Priority review",IF(R2=TRUE,"High cost",IF(S2=TRUE,"Low quality","Benchmark")))',
]];
hospitals.getRange(`U2:U${hospitalEnd}`).fillDown();
hospitals.getRange(`A1:U${hospitalEnd}`).format.font = { name: font, size: 9, color: "#22313B" };
hospitals.getRange("A1:U1").format = {
  fill: navy,
  font: { name: font, bold: true, color: "#FFFFFF" },
  wrapText: true,
};
hospitals.getRange(`H2:J${hospitalEnd}`).format.numberFormat = "0.00";
hospitals.getRange(`K2:L${hospitalEnd}`).format.numberFormat = "#,##0";
hospitals.getRange(`M2:M${hospitalEnd}`).format.numberFormat = "0.0%";
hospitals.getRange(`N2:N${hospitalEnd}`).format.numberFormat = "$#,##0";
hospitals.getRange(`O2:Q${hospitalEnd}`).format.numberFormat = "0.0%";
hospitals.getRange(`A2:U${hospitalEnd}`).conditionalFormats.addCustom("=$T2=TRUE", {
  fill: red,
  font: { color: "#842029", bold: true },
});
hospitals.getRange(`A2:U${hospitalEnd}`).conditionalFormats.addCustom(
  '=AND($T2<>TRUE,OR($R2=TRUE,$S2=TRUE))',
  { fill: amber, font: { color: "#7A4B00" } },
);
hospitals.tables.add(`A1:U${hospitalEnd}`, true, "HospitalComparisonTable").style = "TableStyleMedium2";
hospitals.freezePanes.freezeRows(1);
hospitals.freezePanes.freezeColumns(2);

const stateEnd = payload.states.length + 1;
const stateHeaders = [
  "State", "Hospitals", "Hospitals with rating", "Median overall rating", "Median HCAHPS star",
  "Median MSPB ratio", "Median expense / discharge", "High-cost flag rate",
  "Low-quality flag rate", "Priority hospitals",
];
states.getRange("A1:J1").values = [stateHeaders];
states.getRange(`A2:J${stateEnd}`).values = payload.states.map((row) => [
  row.state, row.hospitals, row.hospitals_with_rating, row.median_overall_rating,
  row.median_hcahps_star, row.median_mspb_ratio, row.median_operating_expense_per_discharge,
  row.high_cost_flag_rate, row.low_quality_flag_rate, row.review_priority_hospitals,
]);
states.getRange(`A1:J${stateEnd}`).format.font = { name: font, size: 10, color: "#22313B" };
states.getRange("A1:J1").format = {
  fill: navy,
  font: { name: font, bold: true, color: "#FFFFFF" },
  wrapText: true,
};
states.getRange(`B2:C${stateEnd}`).format.numberFormat = "#,##0";
states.getRange(`D2:F${stateEnd}`).format.numberFormat = "0.00";
states.getRange(`G2:G${stateEnd}`).format.numberFormat = "$#,##0";
states.getRange(`H2:I${stateEnd}`).format.numberFormat = "0.0%";
states.getRange(`J2:J${stateEnd}`).format.numberFormat = "#,##0";
states.tables.add(`A1:J${stateEnd}`, true, "StateBenchmarkTable").style = "TableStyleMedium2";
states.freezePanes.freezeRows(1);

summary.getRange("A1:N28").format.font = { name: font, size: 10, color: "#22313B" };
summary.mergeCells("A2:N2");
summary.getRange("A2").values = [["CMS Hospital Quality & Cost Benchmarking"]];
summary.getRange("A2").format = {
  fill: navy,
  font: { name: font, size: 18, bold: true, color: "#FFFFFF" },
  verticalAlignment: "center",
};
summary.mergeCells("A3:N3");
summary.getRange("A3").values = [[
  "Hospital-level comparison of CMS quality, patient experience, utilization, and 2023 cost reports",
]];
summary.getRange("A3").format.font = { name: font, size: 10, italic: true, color: "#5C6D78" };

summary.getRange("A5:N5").values = [[
  "Portfolio scope", "Value", "", "", "Coverage", "Value", "", "", "Benchmark", "Value", "", "", "Review queue", "Value",
]];
for (const cell of ["A5:B5", "E5:F5", "I5:J5", "M5:N5"]) {
  summary.getRange(cell).format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
}
summary.getRange("A6:B9").values = [
  ["Hospitals", null],
  ["States / territories", null],
  ["Small hospitals", null],
  ["Large hospitals", null],
];
summary.getRange("B6").formulas = [[`=COUNTA('Hospital Comparison'!A2:A${hospitalEnd})`]];
summary.getRange("B7").formulas = [[`=COUNTA('State Benchmarks'!A2:A${stateEnd})`]];
summary.getRange("B8").formulas = [[`=COUNTIF('Hospital Comparison'!G2:G${hospitalEnd},"Small (<100 beds)")`]];
summary.getRange("B9").formulas = [[`=COUNTIF('Hospital Comparison'!G2:G${hospitalEnd},"Large (300+ beds)")`]];

summary.getRange("E6:F9").values = [
  ["Overall rating reported", null],
  ["Expense / discharge reported", null],
  ["HCAHPS star reported", null],
  ["MSPB reported", null],
];
summary.getRange("F6").formulas = [[`=COUNT('Hospital Comparison'!H2:H${hospitalEnd})`]];
summary.getRange("F7").formulas = [[`=COUNT('Hospital Comparison'!N2:N${hospitalEnd})`]];
summary.getRange("F8").formulas = [[`=COUNT('Hospital Comparison'!I2:I${hospitalEnd})`]];
summary.getRange("F9").formulas = [[`=COUNT('Hospital Comparison'!J2:J${hospitalEnd})`]];

summary.getRange("I6:J9").values = [
  ["Median overall rating", null],
  ["Median HCAHPS star", null],
  ["Median MSPB ratio", null],
  ["Median expense / discharge", null],
];
summary.getRange("J6").formulas = [[`=MEDIAN('Hospital Comparison'!H2:H${hospitalEnd})`]];
summary.getRange("J7").formulas = [[`=MEDIAN('Hospital Comparison'!I2:I${hospitalEnd})`]];
summary.getRange("J8").formulas = [[`=MEDIAN('Hospital Comparison'!J2:J${hospitalEnd})`]];
summary.getRange("J9").formulas = [[`=MEDIAN('Hospital Comparison'!N2:N${hospitalEnd})`]];

summary.getRange("M6:N9").values = [
  ["High-cost flags", null],
  ["Low-quality flags", null],
  ["Priority review", null],
  ["Priority share", null],
];
summary.getRange("N6").formulas = [[`=COUNTIF('Hospital Comparison'!U2:U${hospitalEnd},"High cost")+COUNTIF('Hospital Comparison'!U2:U${hospitalEnd},"Priority review")`]];
summary.getRange("N7").formulas = [[`=COUNTIF('Hospital Comparison'!U2:U${hospitalEnd},"Low quality")+COUNTIF('Hospital Comparison'!U2:U${hospitalEnd},"Priority review")`]];
summary.getRange("N8").formulas = [[`=COUNTIF('Hospital Comparison'!U2:U${hospitalEnd},"Priority review")`]];
summary.getRange("N9").formulas = [["=N8/B6"]];

for (const range of ["A6:B9", "E6:F9", "I6:J9", "M6:N9"]) {
  summary.getRange(range).format.fill = paleBlue;
}
summary.getRange("B6:B9").format.numberFormat = "#,##0";
summary.getRange("F6:F9").format.numberFormat = "#,##0";
summary.getRange("J6:J8").format.numberFormat = "0.00";
summary.getRange("J9").format.numberFormat = "$#,##0";
summary.getRange("N6:N8").format.numberFormat = "#,##0";
summary.getRange("N9").format.numberFormat = "0.0%";

const topStates = [...payload.states]
  .sort((a, b) => b.review_priority_hospitals - a.review_priority_hospitals)
  .slice(0, 10);
summary.getRange("A12:J22").values = [
  ["State", "Hospitals", "Rated", "Median rating", "Median HCAHPS", "Median MSPB", "Median expense/discharge", "Priority hospitals", "High-cost rate", "Low-quality rate"],
  ...topStates.map((row) => [
    row.state, row.hospitals, row.hospitals_with_rating, row.median_overall_rating,
    row.median_hcahps_star, row.median_mspb_ratio, row.median_operating_expense_per_discharge,
    row.review_priority_hospitals, row.high_cost_flag_rate, row.low_quality_flag_rate,
  ]),
];
summary.getRange("A11").values = [["States with the largest priority review queue"]];
summary.getRange("A11").format.font = { name: font, size: 12, bold: true, color: navy };
summary.getRange("A12:J12").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, wrapText: true };
summary.getRange("B13:C22").format.numberFormat = "#,##0";
summary.getRange("D13:F22").format.numberFormat = "0.00";
summary.getRange("G13:G22").format.numberFormat = "$#,##0";
summary.getRange("H13:H22").format.numberFormat = "#,##0";
summary.getRange("I13:J22").format.numberFormat = "0.0%";

const chart = summary.charts.add("bar", [summary.getRange("A12:A22"), summary.getRange("H12:H22")]);
chart.title = "Priority-review hospitals by state";
chart.titleTextStyle.typeface = font;
chart.hasLegend = false;
chart.xAxis = { numberFormatCode: "0", numberFormatSourceLinked: false, textStyle: { typeface: font } };
chart.yAxis = { textStyle: { typeface: font, fontSize: 9 } };
chart.setPosition("L12", "N23");
if (chart.series.items.length) chart.series.items[0].fill = blue;

summary.getRange("A25:B25").values = [["Interpretation note", ""]];
summary.getRange("A25").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
summary.mergeCells("B25:N27");
summary.getRange("B25").values = [[
  "Peer flags use hospital type and bed-size groups, require at least 10 reported peers, and identify the top cost decile / bottom rating decile. They are descriptive review signals—not clinical judgments, causal findings, or a universal hospital score. Source periods and denominators differ by CMS product.",
]];
summary.getRange("B25").format = { fill: paleBlue, wrapText: true, verticalAlignment: "center" };

const qualityEnd = payload.quality.length + 2;
quality.mergeCells("A1:E1");
quality.getRange("A1").values = [["Data Quality Results"]];
quality.getRange("A1").format.font = { name: font, size: 15, bold: true, color: navy };
quality.getRange("A2:E2").values = [["Check", "Severity", "Failed rows", "Status", "Definition"]];
quality.getRange(`A3:E${qualityEnd}`).values = payload.quality.map((row) => [
  row.check_name, row.severity, row.failed_rows, row.status, row.detail,
]);
quality.getRange("A2:E2").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
quality.getRange(`A1:E${qualityEnd}`).format.font = { name: font, size: 10, color: "#22313B" };
quality.getRange("A2:E2").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
quality.getRange(`A3:E${qualityEnd}`).conditionalFormats.addCustom('=$D3="FAIL"', { fill: red, font: { color: "#842029", bold: true } });
quality.getRange(`A3:E${qualityEnd}`).conditionalFormats.addCustom('=$B3="warning"', { fill: amber, font: { color: "#7A4B00" } });
quality.freezePanes.freezeRows(2);

const definitionRows = [
  ["Overall rating", "CMS reported hospital overall rating", "1–5 stars", "Hospital General Information", "Eligibility and suppression apply."],
  ["HCAHPS summary star", "CMS measure H_STAR_RATING", "1–5 stars", "HCAHPS", "Patient experience, not clinical outcome."],
  ["MSPB ratio", "CMS episode-spending score", "ratio", "Medicare Spending per Beneficiary", "Relative episode spending; not total cost."],
  ["Bed occupancy proxy", "Total inpatient days / available bed days", "%", "2023 Hospital Cost Report", "Not real-time staffed-bed occupancy."],
  ["Expense per discharge", "Operating expense / total discharges", "USD/discharge", "2023 Hospital Cost Report", "Not adjusted for case mix."],
  ["Operating margin proxy", "Net income from service / net patient revenue", "%", "2023 Hospital Cost Report", "Uses submitted accounting fields."],
  ["High-cost peer flag", "Cost peer percentile >= 90th with >=10 peers", "Boolean", "Derived", "Descriptive review signal."],
  ["Low-quality peer flag", "Rating peer percentile <= 10th with >=10 peers", "Boolean", "Derived", "Descriptive review signal."],
  ["Priority flag", "Both high-cost and low-quality flags", "Boolean", "Derived", "No causal or clinical interpretation."],
];
definitions.mergeCells("A1:E1");
definitions.getRange("A1").values = [["KPI Definitions and Official Sources"]];
definitions.getRange("A1").format.font = { name: font, size: 15, bold: true, color: navy };
definitions.getRange("A3:E3").values = [["KPI", "Formula / selection", "Unit", "Source", "Interpretation limit"]];
definitions.getRange("A4:E12").values = definitionRows;
definitions.getRange("A3:E3").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
definitions.getRange("A14:B20").values = [
  ["Official source", "URL"],
  ["Hospital General Information", "https://data.cms.gov/provider-data/dataset/xubh-q36u"],
  ["HCAHPS", "https://data.cms.gov/provider-data/dataset/dgck-syfz"],
  ["Complications and Deaths", "https://data.cms.gov/provider-data/dataset/ynj2-r877"],
  ["Unplanned Hospital Visits", "https://data.cms.gov/provider-data/dataset/632h-zaca"],
  ["Medicare Spending per Beneficiary", "https://data.cms.gov/provider-data/dataset/rrqw-56er"],
  ["Hospital Cost Report", "https://data.cms.gov/provider-compliance/cost-reports/hospital-provider-cost-report"],
];
definitions.getRange("A14:B14").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
definitions.getRange("A1:E20").format.font = { name: font, size: 10, color: "#22313B" };
definitions.getRange("A3:E3").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
definitions.getRange("A14:B14").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
definitions.getRange("A4:A12").format.fill = paleGray;
definitions.freezePanes.freezeRows(3);

summary.getRange("A1:N28").format.verticalAlignment = "center";
summary.getRange("A1:N28").format.autofitRows();
summary.getRange("A:A").format.columnWidth = 24;
summary.getRange("B:B").format.columnWidth = 15;
summary.getRange("C:C").format.columnWidth = 12;
summary.getRange("D:D").format.columnWidth = 16;
summary.getRange("E:E").format.columnWidth = 24;
summary.getRange("F:F").format.columnWidth = 15;
summary.getRange("G:G").format.columnWidth = 24;
summary.getRange("H:H").format.columnWidth = 15;
summary.getRange("I:I").format.columnWidth = 24;
summary.getRange("J:J").format.columnWidth = 15;
summary.getRange("K:L").format.columnWidth = 12;
summary.getRange("M:M").format.columnWidth = 22;
summary.getRange("N:N").format.columnWidth = 15;
summary.getRange("B25:N27").format.rowHeight = 28;

hospitals.getRange("A:A").format.columnWidth = 12;
hospitals.getRange("B:B").format.columnWidth = 34;
hospitals.getRange("C:C").format.columnWidth = 20;
hospitals.getRange("D:D").format.columnWidth = 9;
hospitals.getRange("E:G").format.columnWidth = 23;
hospitals.getRange("H:U").format.columnWidth = 15;
states.getRange("A:J").format.autofitColumns();
states.getRange("A:J").format.autofitRows();
states.getRange("G:G").format.columnWidth = 25;
quality.getRange("A:E").format.autofitRows();
quality.getRange("A:A").format.columnWidth = 42;
quality.getRange("B:D").format.columnWidth = 16;
quality.getRange("E:E").format.columnWidth = 72;
quality.getRange("E:E").format.wrapText = true;
definitions.getRange("A:E").format.autofitRows();
definitions.getRange("A:A").format.columnWidth = 30;
definitions.getRange("B:B").format.columnWidth = 52;
definitions.getRange("C:D").format.columnWidth = 28;
definitions.getRange("E:E").format.columnWidth = 48;
definitions.getRange("B:E").format.wrapText = true;

wb.recalculate();
await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });
const previewRanges = {
  "Executive Summary": "A1:N27",
  "Hospital Comparison": "A1:U25",
  "State Benchmarks": `A1:J${stateEnd}`,
  "Data Quality": `A1:E${qualityEnd}`,
  "KPI Definitions": "A1:E20",
};
for (const [sheetName, range] of Object.entries(previewRanges)) {
  const preview = await wb.render({ sheetName, range, scale: 1, format: "png" });
  const slug = sheetName.toLowerCase().replaceAll(" ", "_");
  await fs.writeFile(`${previewDir}/${slug}.png`, new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(wb);
await output.save(`${outputDir}/cms_hospital_comparison.xlsx`);

const summaryCheck = await wb.inspect({
  kind: "table", range: "Executive Summary!A1:N27", include: "values,formulas",
  tableMaxRows: 30, tableMaxCols: 14,
});
const errorCheck = await wb.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(summaryCheck.ndjson);
console.log(errorCheck.ndjson);

