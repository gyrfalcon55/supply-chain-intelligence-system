import requests

API_URL = "http://127.0.0.1:8000"


def test_supplier_dashboard_api():

    response = requests.get(
        f"{API_URL}/suppliers"
    )

    assert response.status_code == 200

    data = response.json()

    assert "plots" in data
    assert "top5_suppliers" in data["plots"]