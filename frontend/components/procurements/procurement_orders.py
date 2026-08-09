import streamlit as st
import pandas as pd
import requests
import os

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.title("Procurement Orders Page!")

# -----------------------------
# Session State
# -----------------------------

if "planning_date" not in st.session_state:
    st.session_state.planning_date = None


if "orders" not in st.session_state:
    st.session_state.orders = None

if "submitted_orders" not in st.session_state:
    st.session_state.submitted_orders = None

if "approval_result" not in st.session_state:
    st.session_state.approval_result = None


# -----------------------------
# Buttons
# -----------------------------
show_col, submit_col = st.columns(2)

# Fetch Procurement Recommendations
if show_col.button(
    "Show Supplier and Products List",
    icon="📦",
    width="stretch"
):

    response = requests.post(f"{API_URL}/procurement_orders")

    if response.status_code == 200:

        data = response.json()

        st.session_state.orders = pd.DataFrame(data["table"])
        st.session_state.submitted_orders = None
        st.session_state.approval_result = None

    else:
        st.error("Failed to generate Procurement Report")
        st.write(response.text)


# -----------------------------
# Editable Table
# -----------------------------
if st.session_state.orders is not None:

    edited_df = st.data_editor(
        st.session_state.orders,
        hide_index=True,
        num_rows="fixed",
        key="procurement_editor",
        disabled=[
            "Product_ID",
            "Qty_To_Order",
            "Label"
        ],
        column_config={
            "Supplier_Name": st.column_config.TextColumn(
                "Supplier Name ✏️",
                help="Click to edit supplier name"
            )
        }
    )

    if submit_col.button(
        "Submit",
        icon="👍",
        width="stretch"
    ):
        st.session_state.submitted_orders = edited_df.copy()


# -----------------------------
# Submitted Table
# -----------------------------
if st.session_state.submitted_orders is not None:

    st.success("Review the procurement orders before final approval.")

    st.dataframe(
        st.session_state.submitted_orders,
        hide_index=True,
        width="stretch"
    )

    if st.button(
        "Final Approve",
        icon="⭐",
        width="stretch",
        disabled=st.session_state.approval_result is not None
    ):

        df = pd.DataFrame(st.session_state.submitted_orders)

        if st.session_state.planning_date is None:
            st.error("Planning date not found. Run the planning cycle first.")
            st.stop()

        response = requests.post(
            f"{API_URL}/procurement_orders/final_list",
            json={
                "planning_date": st.session_state.planning_date,
                "data": df.to_dict(orient="records")
            }
        )

        if response.status_code == 200:

            st.session_state.approval_result = response.json()

            # Optional: Clear tables after successful approval
            st.session_state.planning_date = None
            st.session_state.orders = None
            st.session_state.submitted_orders = None

        else:
            st.error("Failed to approve procurement orders.")
            st.write(response.text)


# -----------------------------
# Approval Results
# -----------------------------
if st.session_state.approval_result is not None:

    result = st.session_state.approval_result

    st.success("Procurement orders processed successfully.")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Blocked Orders",
        result["existing_orders_count"]
    )

    col2.metric(
        "New Orders",
        result["new_orders_count"]
    )

    col3.metric(
        "Approved Orders",
        result["approved_orders"]
    )

    tab1, tab2 = st.tabs(
        [
            "✅ Approved Orders",
            "⚠️ Blocked Orders"
        ]
    )

    with tab1:

        st.dataframe(
            pd.DataFrame(result["new_orders"]),
            hide_index=True,
            width="stretch"
        )

    with tab2:

        st.dataframe(
            pd.DataFrame(result["existing_orders"]),
            hide_index=True,
            width="stretch"
        )