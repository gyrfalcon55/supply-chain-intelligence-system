import streamlit as st
import requests
import pandas as pd
import os

from frontend.components.visuals.plotting import plots

st.title("Welcome to the table viewer")
st.write("- Click the table button to view the table")
st.write("(Note : only 100 records are shown)")



API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def show_table(table_name: str):
    response = requests.post(
        f"{API_URL}/table_view",
        json={
            "table_name": table_name,
            "limit": 100
        }
    )

    if response.status_code == 200:
        data = response.json()
        st.dataframe(
            pd.DataFrame(data["table"]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.error(f"Failed to load {table_name}")
        st.write(response.text)


def sales_plots():
    response = requests.get(
        f"{API_URL}/sales_orders"
    )

    if response.status_code == 200:
        data = response.json()
        plots.top5_prods(data["plots"]["top5_prods"])
        plots.cat_revenue(data["plots"]["revenue_by_cat"])
    else:
        st.error(f"Failed to plot sales_orders")
        st.write(response.text)

def supplier_plots():
    response = requests.get(
        f"{API_URL}/suppliers"
    )

    if response.status_code == 200:
        data = response.json()
        plots.supplier_plot(data["plots"]["top5_suppliers"])
    else:
        st.error(f"Failed to plot suppliers")
        st.write(response.text)


def ineventory_plots():
    response = requests.get(
        f"{API_URL}/inventory"
    )

    if response.status_code == 200:
        data = response.json()
        plots.ineventory_cat(data["plots"]["inventory_by_cat"])
    else:
        st.error(f"Failed to plot suppliers")
        st.write(response.text)



suppliers, inventory, sales_orders = st.columns(3)

if suppliers.button("Suppliers", icon="🚚",width='stretch'):
    show_table("suppliers")
    supplier_plots()


if inventory.button("Inventory", icon="📦", width='stretch'):
    show_table("inventory")
    ineventory_plots()

if sales_orders.button("sales_orders", icon="📈", width='stretch'):
    show_table("sales_orders")
    sales_plots()