from cms_hospital_benchmark.provider_api import ProviderDataClient


def test_fetch_paginates_and_preserves_rows(monkeypatch):
    client = ProviderDataClient(page_size=2)
    pages = {
        0: {"count": 3, "results": [{"facility_id": "000001"}, {"facility_id": "000002"}]},
        2: {"count": 3, "results": [{"facility_id": "000003"}]},
    }
    monkeypatch.setattr(client, "_page", lambda _dataset, offset: pages[offset])
    frame = client.fetch("example")
    assert frame["facility_id"].tolist() == ["000001", "000002", "000003"]
    client.close()
