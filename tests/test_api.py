import os

import pandas as pd
import pytest
import requests


API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)


# ============================================================
# Root
# ============================================================

def test_home_api():

    response = requests.get(
        f"{API_URL}/"
    )

    assert response.status_code == 200

    data = response.json()

    assert "message" in data
    assert data["message"] == "Backend running"


# ============================================================
# Table APIs
# ============================================================

@pytest.mark.parametrize(
    "table",
    [
        "inventory",
        "sales_orders",
        "suppliers"
    ]
)
def test_table_view_api(table):

    response = requests.post(
        f"{API_URL}/table_view",
        json={
            "table_name": table,
            "limit": 10,
            "thread_id": "1"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "table" in data

    df = pd.DataFrame(
        data["table"]
    )

    assert not df.empty


# ============================================================
# Dashboard APIs
# ============================================================

def test_sales_dashboard_api():

    response = requests.get(
        f"{API_URL}/sales_orders"
    )

    assert response.status_code == 200

    data = response.json()

    assert "plots" in data
    assert "top5_prods" in data["plots"]
    assert "revenue_by_cat" in data["plots"]


def test_supplier_dashboard_api():

    response = requests.get(
        f"{API_URL}/suppliers"
    )

    assert response.status_code == 200

    data = response.json()

    assert "plots" in data
    assert "top5_suppliers" in data["plots"]


def test_inventory_dashboard_api():

    response = requests.get(
        f"{API_URL}/inventory"
    )

    assert response.status_code == 200

    data = response.json()

    assert "plots" in data
    assert "inventory_by_cat" in data["plots"]


# ============================================================
# Report APIs
# ============================================================

@pytest.mark.parametrize(
    "report_name,expected_key",
    [
        ("Inventory Report", "stock_summary"),
        ("Supplier Report", "stock_summary"),
        ("Recommended Suppliers", "consolidated"),
    ]
)
def test_report_api(report_name, expected_key):

    response = requests.post(
        f"{API_URL}/reports",
        json={
            "report_name": report_name
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert expected_key in data


# ============================================================
# Procurement
# ============================================================

def test_procurement_recommendations_api():

    response = requests.post(
        f"{API_URL}/procurement_orders"
    )

    assert response.status_code == 200

    data = response.json()

    assert "table" in data

    df = pd.DataFrame(
        data["table"]
    )

    assert not df.empty


# ============================================================
# Simulation
# ============================================================

def test_simulation_run_day_api():

    response = requests.post(
        f"{API_URL}/simulation/run_day"
    )

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "status",
        "current_date",
        "planning_due",
        "planning_day",
        "days_remaining"
    }

    missing_fields = (
        expected_fields
        - set(data.keys())
    )

    assert not missing_fields, (
        f"Missing fields: {missing_fields}"
    )


# ============================================================
# ML Pipeline
# ============================================================

def test_ml_pipeline_start_api():

    response = requests.post(
        f"{API_URL}/ml_pipeline"
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert isinstance(
        data["job_id"],
        str
    )
    assert len(data["job_id"]) > 0