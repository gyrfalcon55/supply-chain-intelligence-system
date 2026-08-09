"""
forecasting_pipeline.py

Deterministic, sequential inventory/forecast/procurement analysis pipeline.

No LLM calls, no runtime decisions, no LangGraph. Every step is a plain
Python function executed in a fixed order:

    load data -> label stock status -> summarize -> pull product lists
    -> pull best suppliers -> consolidate -> print report

This intentionally mirrors the architecture doc: the Forecasting/Procurement
side of the system should be fully auditable and reproducible for the same
inputs. If you later add an LLM step, it should only wrap the final report
in natural language -- it should never feed back into classification or
supplier selection.
"""

from sqlalchemy import text
import numpy as np
import pandas as pd

from backend.services.db_service import Load_Data


from utils.db_crud import save_to_db, load_from_db




class reports:

    def __init__(self):
        load_df = Load_Data()
        self.ACTIONABLE_LABELS = ["CRITICAL", "REORDER_NOW", "AT_RISK"]
        self.ALL_LABELS = ["CRITICAL", "REORDER_NOW", "AT_RISK", "SUFFICIENT", "NEEDS_REVIEW"]
        self.inventory_df = load_df.load("inventory")
        self.forecast_df = load_df.load("forecast")


    def label_data(self) -> pd.DataFrame:
        """
        Compare current inventory against next-period forecasted demand and
        classify every product into a stockout risk bucket.

        FIX: original merge used `on=forecast['unique_id']` which passes a
        Series instead of a column name -- pandas silently mishandles this and
        drops/duplicates rows. Using the column name directly instead.
        """

        loader = Load_Data()

        inventory_df = loader.load("inventory")
        forecast_df = loader.load("forecast")

        stockout = inventory_df.merge(
            right= forecast_df,
            on= forecast_df['unique_id'],
            how="left",
        )[["unique_id", "Current_Stock", "Reorder_Level", "Safety_Stock", "CrostonClassic"]]

        stockout["stockout"] = (stockout["Current_Stock"] - stockout["CrostonClassic"]).round()

        conditions = [
            # Already at/below safety stock
            stockout["Current_Stock"] <= stockout["Safety_Stock"],

            # Below reorder level but above safety stock
            (
                (stockout["Current_Stock"] > stockout["Safety_Stock"])
                & (stockout["Current_Stock"] <= stockout["Reorder_Level"])
            ),

            # Above reorder level now, but forecasted demand will push it
            # into safety stock before the next cycle
            (
                (stockout["Current_Stock"] > stockout["Reorder_Level"])
                & (
                    stockout["Current_Stock"] - stockout["CrostonClassic"]
                    <= stockout["Safety_Stock"]
                )
            ),

            # Healthy: stays above safety stock even after forecasted demand
            (
                (stockout["Current_Stock"] > stockout["Reorder_Level"])
                & (
                    stockout["Current_Stock"] - stockout["CrostonClassic"]
                    > stockout["Safety_Stock"]
                )
            ),
        ]

        choices = ["CRITICAL", "REORDER_NOW", "AT_RISK", "SUFFICIENT"]

        # Anything that doesn't match a rule (e.g. NaNs from an unmatched
        # product after the merge) is surfaced as NEEDS_REVIEW rather than
        # silently defaulting to a "safe" label.
        stockout["stockout_label"] = np.select(conditions, choices, default="NEEDS_REVIEW")

        save_to_db(stockout, "labeled_inventory_data", "master_data")

        return stockout


    # ---------------------------------------------------------------------------
    # Step 3: Summarize
    # ---------------------------------------------------------------------------

    def stock_summary(self) -> dict:
        """Count and percentage breakdown per stockout label."""
        summary = {}
        df = self.label_data()
        total = len(df)
        for label in self.ALL_LABELS:
            subset = df[df["stockout_label"] == label]
            summary[label] = {
                "products_count": int(len(subset)),
                "pct": float(round(len(subset) / total * 100, 1)) if total else 0.0,
            }
        return summary


    # ---------------------------------------------------------------------------
    # Step 4: Product lists per label
    # ---------------------------------------------------------------------------

    def get_product_ids(self,label: str) -> list:
        """
        Return product IDs for a given stockout label.

        FIX: original built the WHERE clause with an f-string
        (SQL injection risk). Using a bound parameter instead.
        """
        query = text("""
            SELECT *
            FROM master_data.labeled_inventory_data
            WHERE "stockout_label" = :label;
        """)
        inventory_df = load_from_db(query, "labeled_inventory_table", params={"label": label})
        return inventory_df["unique_id"].unique().tolist()


    def get_all_product_ids(self) -> dict:
        return {label: self.get_product_ids(label) for label in self.ALL_LABELS}


    # ---------------------------------------------------------------------------
    # Step 5: Best supplier per product (actionable labels only)
    # ---------------------------------------------------------------------------

    def get_supplier_details(self,label: str) -> pd.DataFrame:
        """
        Best preferred supplier per product for a given label, ranked by
        preferred status then on-time delivery rate.
        """
        query = text("""
            WITH ranked_suppliers AS (
                SELECT
                    p."Product_ID",
                    s."Supplier_ID",
                    s."Supplier_Name",
                    s."On_Time_Delivery_Rate",
                    s."Is_Preferred_Supplier",

                    ROW_NUMBER() OVER (
                        PARTITION BY p."Product_ID"
                        ORDER BY
                            s."Is_Preferred_Supplier" DESC,
                            s."On_Time_Delivery_Rate" DESC
                    ) AS rn

                FROM master_data.labeled_inventory_data l

                JOIN raw_data.procurement_orders p
                    ON l."unique_id" = p."Product_ID"

                JOIN raw_data.suppliers s
                    ON p."Supplier_ID" = s."Supplier_ID"

                WHERE l."stockout_label" = :label
                AND s."Is_Preferred_Supplier" = 1
            )
            SELECT
                "Product_ID",
                "Supplier_ID",
                "Supplier_Name",
                "On_Time_Delivery_Rate",
                "Is_Preferred_Supplier"
            FROM ranked_suppliers
            WHERE rn = 1
        """)
        return load_from_db(query, "best_supplier_details", params={"label": label})


    def get_suppliers_for_actionable_labels(self) -> dict:
        """
        Only CRITICAL / REORDER_NOW / AT_RISK need a supplier lookup --
        SUFFICIENT products don't require action, so we don't spend a query
        on them here.

        NOTE: products with no *preferred* supplier will be absent from these
        results (see WHERE Is_Preferred_Supplier = 1 above). That's a
        deliberate business rule, not a bug -- but it means "products_count"
        from stock_summary() and the row count here can legitimately differ.
        Any product missing here should be called out in the report rather
        than silently dropped.
        """
        return {label: self.get_supplier_details(label) for label in self.ACTIONABLE_LABELS}


    # ---------------------------------------------------------------------------
    # Step 6: Consolidate -- group products under shared suppliers
    # ---------------------------------------------------------------------------

    def consolidate_by_supplier(self) -> dict:
        """
        For each actionable label, group products by Supplier_ID so a single
        supplier with multiple qualifying products becomes one consolidated
        order line instead of several duplicate ones.
        """
        all_suppliers = self.get_suppliers_for_actionable_labels()
        consolidated = {}
        for label, df in all_suppliers.items():
            if df is None or len(df) == 0:
                consolidated[label] = []
                continue

            grouped = (
                df.groupby(["Supplier_ID", "Supplier_Name", "On_Time_Delivery_Rate"])["Product_ID"]
                .apply(list)
                .reset_index()
                .rename(columns={"Product_ID": "Products"})
            )
            grouped["Product_Count"] = grouped["Products"].apply(len)
            consolidated[label] = grouped.sort_values("Product_Count", ascending=False).to_dict("records")

        return consolidated


    # ---------------------------------------------------------------------------
    # Step 7: Report
    # ---------------------------------------------------------------------------


    


