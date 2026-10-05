from cms_hospital_benchmark.cost_report_api import CostReportClient


def test_cost_report_pagination_stops_on_short_page(monkeypatch):
    client = CostReportClient(page_size=2)
    pages = {
        0: [{"Provider CCN": "000001"}, {"Provider CCN": "000002"}],
        2: [{"Provider CCN": "000003"}],
    }
    monkeypatch.setattr(client, "_page", lambda offset: pages[offset])
    frame = client.fetch()
    assert len(frame) == 3
    assert frame.iloc[-1]["Provider CCN"] == "000003"
    client.close()

