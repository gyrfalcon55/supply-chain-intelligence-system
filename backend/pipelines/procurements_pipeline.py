from backend.pipelines.forecasting_pipeline import reports

import streamlit as st

from backend.services.db_service import Load_Data

load_df = Load_Data()

import pandas as pd

obj = reports()

def recommended_suppliers():

    df = obj.consolidate_by_supplier()

    inventory_df =  load_df.load("inventory")
    result = []

    for key, value in df.items():
        for i in value:
            for x in range(len(i['Products'])):
                prod = inventory_df[inventory_df['Product_ID'] == i['Products'][x]][['Current_Stock','Reorder_Level','Safety_Stock','Unit_Cost']]
                qty_to_order = (prod['Reorder_Level'] + prod['Safety_Stock'] - prod['Current_Stock']).iloc[0]
                if key == "CRITICAL" or key == "CRITICAL 🔴":
                    key = "CRITICAL 🔴"
                elif key == "REORDER_NOW" or key == "REORDER_NOW 🟡":
                    key = "REORDER_NOW 🟡"
                else:
                    key = "AT_RISK 🔵"
                unit_cost = prod['Unit_Cost'].iloc[0]
                result.append({
                    'Supplier_ID':i['Supplier_ID'],
                    'Product_ID': i['Products'][x],
                    'Qty_To_Order': qty_to_order,
                    'Unit_Cost': unit_cost,
                    'Total_Cost':round(unit_cost * qty_to_order,2),
                    'Label':key
                })

    result_df = pd.DataFrame(result)

    return result_df


existing_proc = load_df.load("procurement")


def return_existing_orders(new_proc):
    """
    Returns orders from new_proc whose Product_ID already has an In_Transit order.
    """
    in_transit = existing_proc[existing_proc['Order_Status'] == 'In_Transit'][['PO_ID','Supplier_ID','Product_ID','Order_Status','Order_Date']]
    seen = set(in_transit['Product_ID'])
    filtered_df = new_proc[
        new_proc["Product_ID"].isin(seen)
    ].copy().reset_index(drop=True)

    return filtered_df.merge(
        in_transit,
        on="Product_ID",
        how="left",
        suffixes=("_Recommended", "_Existing")
    )[['PO_ID_Existing','Supplier_ID_Existing','Product_ID','Order_Status_Existing','Order_Date_Existing']]

def return_new_orders(new_proc):
    """
    Returns orders from new_proc whose Product_ID does NOT have an In_Transit order.
    """
    in_transit = existing_proc[existing_proc['Order_Status'] == 'In_Transit']
    seen = set(in_transit['Product_ID'])
    filtered_df = new_proc[
        ~new_proc["Product_ID"].isin(seen)
    ].copy().reset_index(drop=True)

    return filtered_df
