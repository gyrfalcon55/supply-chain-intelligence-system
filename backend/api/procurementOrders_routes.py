from fastapi import APIRouter
from backend.pipelines.procurements_pipeline import recommended_suppliers,return_existing_orders,return_new_orders
from backend.schemas.request import FinalProcurementList
from utils.db_crud import append_to_db
import pandas as pd
from configs.config import load_config
from backend.services.procurement_service import generate_procurement_order_ids
from backend.services.db_service import Load_Data

import numpy as np

config = load_config()

router = APIRouter()

@router.post("/procurement_orders")
def procurement_orders():

    rcd_sup = recommended_suppliers()

    return {
        "table":rcd_sup.to_dict(orient="records")
    }

@router.post("/procurement_orders/final_list")
def procurement_orders(requests: FinalProcurementList):
    load_df = Load_Data()
    
    existing_procurements = load_df.load("procurement")

    approved_orders  = requests.data
    approved_orders  = pd.DataFrame(approved_orders)

    approved_orders.drop(columns=['Label'],inplace=True)

    approved_orders["Order_Date"] = pd.to_datetime(
        requests.planning_date,
        errors="raise"
    )
    approved_orders['Order_Status'] = "Pending"

    approved_orders = generate_procurement_order_ids(
        approved_orders,
        existing_orders_df=existing_procurements
    )

    lead_times = np.random.randint(4, 6, len(approved_orders))

    approved_orders["Expected_Delivery_Date"] = (
        approved_orders["Order_Date"]
        + pd.to_timedelta(lead_times, unit="D")
    )

    approved_orders["Actual_Delivery_Date"] = pd.NaT

    new_orders = return_new_orders(approved_orders)
    existing_orders = return_existing_orders(approved_orders)

    append_to_db(new_orders,'procurement_orders','procurements_data')

    return {
        "new_orders_count":len(new_orders),
        "existing_orders_count":len(existing_orders),
        "approved_orders":len(approved_orders),
        "new_orders":new_orders.to_dict(orient='records'),
        "existing_orders":existing_orders.to_dict(orient='records')
    }




