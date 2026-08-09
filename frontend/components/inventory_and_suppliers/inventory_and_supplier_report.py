import streamlit as st
import requests
from frontend.components.inventory_and_suppliers.summary_generator import inventory_summary_ui, supplier_report_ui, consolidated_orders_ui
import os

st.title("Inventory and Supplier Reports")


inventory, supplier, recommended_suppliers = st.columns(3)

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def inventory_report():
    response = requests.post(
        f"{API_URL}/reports",
        json={
            "report_name":"Inventory Report"
        }
    )
    data = response.json()
    if response.status_code == 200:
        inventory_summary_ui(data["stock_summary"])
    else:
        st.error(f"Failed to generate Inventory Report")
        st.write(response.text)

def consolidated_supplier_report():
    response = requests.post(
        f"{API_URL}/reports",
        json={
            "report_name":"Recommended Suppliers"
        }
    )
    data = response.json()
    if response.status_code == 200:
        consolidated_orders_ui(data["consolidated"])
    else:
        st.error(f"Failed to generate Inventory Report")
        st.write(response.text)

def supplier_report():
    response = requests.post(
        f"{API_URL}/reports",
        json={
            "report_name":"Supplier Report"
        }
    )
    data = response.json()
    if response.status_code == 200:
        supplier_report_ui(data["stock_summary"],data["all_suppliers"])
    else:
        st.error(f"Failed to generate Inventory Report")
        st.write(response.text)   

if inventory.button("Inventory Report",icon="📦",width='stretch'):
    st.write("Inventory Report")
    inventory_report()

if supplier.button("Supplier Report",icon="🚚",width='stretch'):
    st.write("supplier Report")
    supplier_report()

if recommended_suppliers.button("Recommended Suppliers",icon="⭐",width='stretch'):
    st.write("Recommended Suppliers Report")
    consolidated_supplier_report()