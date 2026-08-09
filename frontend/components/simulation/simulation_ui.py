import requests
import streamlit as st
from frontend.services.pages_paths import PROCUREMENT_ORDERS_PAGE_PATH


import os

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.title("📅 Sales Simulation")

st.write(
    """
    Simulate one business day.

    Every click represents one simulated day.
    After every 7 days, the planning pipeline is triggered and
    procurement recommendations are generated for approval.
    """
)

# -----------------------------------------
# Initialize session state
# -----------------------------------------

if "planning_date" not in st.session_state:
    st.session_state.planning_date = None

if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None

# -----------------------------------------
# Run Simulation
# -----------------------------------------

if st.button(
    "Simulate One Day",
    icon="📈",
    use_container_width=True
):

    with st.spinner("Running sales simulation..."):

        response = requests.post(
            f"{API_URL}/simulation/run_day"
        )

    if response.status_code == 200:

        data = response.json()

        st.session_state.simulation_result = data

        if "planning_date" in data:
            st.session_state.planning_date = data["planning_date"]   
    else:

        st.error("Failed to run simulation.")

# -----------------------------------------
# Display Results
# -----------------------------------------

if st.session_state.simulation_result is not None:

    result = st.session_state.simulation_result

    st.success(result["status"])

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Current Simulation Date",
            result["current_date"]
        )

    with col2:
        st.metric(
            "Planning Required",
            "YES" if result["planning_due"] else "NO"
        )

    st.metric(
        "Planning Cycle",
        f"{result['planning_day']} / 7"
    )

    st.metric(
        "Days Remaining",
        result["days_remaining"]
    )

    # -----------------------------------------
    # Planning Due
    # -----------------------------------------

    if result["planning_due"]:

        st.warning(
            """
            Weekly planning cycle completed.

            Procurement recommendations have been generated.

            Please review and approve the procurement orders.
            """
        )

        if st.button(
            "Open Procurement Approval",
            icon="🛒",
            use_container_width=True,
            key="open_procurement"
        ):

            st.switch_page(PROCUREMENT_ORDERS_PAGE_PATH)

    else:

        st.info(
            "No procurement planning required today."
        )