import pandas as pd
import streamlit as st




def inventory_summary_ui(summary):
    st.header("📦 Inventory Status Summary")

    # Metrics
    cols = st.columns(len(summary))

    for col, (label, stats) in zip(cols, summary.items()):
        col.metric(
            label,
            stats["products_count"],
            f"{stats['pct']:.1f}%"
        )

    st.divider()

    # Detailed table
    data = [
        {
            "Inventory Status": label,
            "Products": stats["products_count"],
            "Percentage (%)": round(stats["pct"], 2),
        }
        for label, stats in summary.items()
    ]

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True,
        hide_index=True,
    )


def supplier_report_ui(summary, all_suppliers, sample_size=5):

    st.title("🚛 Supplier Report")

    for label, suppliers in all_suppliers.items():

        expected = summary[label]["products_count"]

        # Handle DataFrame
        if isinstance(suppliers, pd.DataFrame):
            df = suppliers.copy()

        # Handle JSON returned from FastAPI
        elif isinstance(suppliers, list):
            df = pd.DataFrame(suppliers)

        else:
            df = pd.DataFrame()

        with st.expander(f"📦 {label}", expanded=True):

            if df.empty:
                st.warning(
                    f"No suppliers found.\n\n"
                    f"Expected Products: **{expected}**"
                )
                continue

            found = len(df)

            avg_rate = df["On_Time_Delivery_Rate"].mean() * 100
            supplier_count = df["Supplier_Name"].nunique()

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Products with Supplier",
                f"{found}/{expected}"
            )

            c2.metric(
                "Avg On-Time Delivery",
                f"{avg_rate:.1f}%"
            )

            c3.metric(
                "Distinct Suppliers",
                supplier_count
            )

            if found < expected:
                st.info(
                    f"{expected-found} product(s) do not have a preferred supplier."
                )
            else:
                st.success("Every product has a preferred supplier.")

            sample_df = (
                df[
                    [
                        "Product_ID",
                        "Supplier_Name",
                        "On_Time_Delivery_Rate",
                    ]
                ]
                .head(sample_size)
                .copy()
            )

            sample_df["On_Time_Delivery_Rate"] *= 100

            sample_df.rename(
                columns={
                    "Product_ID": "Product ID",
                    "Supplier_Name": "Supplier",
                    "On_Time_Delivery_Rate": "On-Time Delivery (%)",
                },
                inplace=True,
            )

            st.dataframe(
                sample_df,
                use_container_width=True,
                hide_index=True,
            )


def consolidated_orders_ui(consolidated):
    st.header("🛒 Consolidated Procurement Recommendations")

    for label, rows in consolidated.items():

        with st.expander(
            f"📦 {label} ({len(rows)} Supplier Order{'s' if len(rows) != 1 else ''})",
            expanded=True,
        ):

            if not rows:
                st.success("✅ Nothing to order.")
                continue

            for row in rows:

                # ---------- Supplier Details ----------
                col1, col2, col3 = st.columns([5, 2, 1])

                with col1:
                    st.markdown(f"**🏢 {row['Supplier_Name']}**")

                with col2:
                    st.markdown(
                        f"**⏱ {row['On_Time_Delivery_Rate'] * 100:.1f}%**"
                    )
                    st.caption("On-Time Delivery")

                with col3:
                    st.markdown(f"**📦 {row['Product_Count']}**")
                    st.caption("Products")

                # ---------- Product Table ----------
                products = row["Products"]

                if isinstance(products, str):
                    products = [p.strip() for p in products.split(",")]

                st.dataframe(
                    pd.DataFrame({"Product ID": products}),
                    use_container_width=True,
                    hide_index=True,
                )

                st.markdown("---")

