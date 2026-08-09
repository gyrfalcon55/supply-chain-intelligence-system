import pandas as pd

def generate_procurement_order_ids(new_orders_df: pd.DataFrame,existing_orders_df = None) -> pd.DataFrame:
    """
    Generate sequential PO_IDs for new procurement orders.

    Parameters
    ----------
    new_orders_df : pd.DataFrame
        Newly approved procurement orders.

    existing_orders_df : pd.DataFrame
        Existing procurement_orders table from the database.

    Returns
    -------
    pd.DataFrame
        New orders with PO_ID assigned.
    """

    new_orders_df = new_orders_df.copy()

    # First run: no procurement orders yet
    if existing_orders_df is None or existing_orders_df.empty:
        last_id = 0
    else:
        last_id = (
            existing_orders_df["PO_ID"]
            .str.replace("PO", "", regex=False)
            .astype(int)
            .max()
        )

    new_orders_df.insert(
        0,
        "PO_ID",
        [
            f"PO{i:05d}"
            for i in range(last_id + 1, last_id + len(new_orders_df) + 1)
        ],
    )

    return new_orders_df
