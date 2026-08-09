import streamlit as st
import requests
from frontend.services.pages_paths import AGENT_PAGE_PATH, TABLE_VIEW_PAGE_PATH, INVENTORY_SUPPLIER_REPORT_PAGE_PATH, PROCUREMENT_ORDERS_PAGE_PATH, SIMULATION_PAGE_PATH, ML_PIPELINE_PAGE_PATH 

pg = st.navigation([
    st.Page(AGENT_PAGE_PATH,title="Analytics Agent", icon="🤖" ),
    st.Page(TABLE_VIEW_PAGE_PATH,title="View Tables", icon="📊"),
    st.Page(INVENTORY_SUPPLIER_REPORT_PAGE_PATH,title="Inventory and Supplier reports", icon="🚚"),
    st.Page(PROCUREMENT_ORDERS_PAGE_PATH,title="Procurement orders", icon="📜"),
    st.Page(SIMULATION_PAGE_PATH,title="Simulation", icon="🛞"),
    st.Page(ML_PIPELINE_PAGE_PATH,title="Run Machine learning", icon="🧪"),
])
pg.run()