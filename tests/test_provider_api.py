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


def test_download_uses_catalog_distribution(monkeypatch):
    class Response:
        content = b"Facility ID,Facility Name\n010001,Example Hospital\n"

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "distribution": [
                    {"mediaType": "text/csv", "downloadURL": "https://example.test/data.csv"}
                ]
            }

    client = ProviderDataClient()
    monkeypatch.setattr(client.client, "get", lambda *_args, **_kwargs: Response())
    frame, url = client.fetch_download("example")
    assert url == "https://example.test/data.csv"
    assert frame.loc[0, "Facility ID"] == "010001"
    client.close()
