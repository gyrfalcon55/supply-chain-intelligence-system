from backend.services.db_service import Load_Data

from backend.schemas.request import TableRequest
from backend.schemas.response import TableResponse
from fastapi import APIRouter
from backend.services.plotting_service import plots_data

router = APIRouter()


@router.post("/table_view", response_model=TableResponse)
def fetch_tables(request: TableRequest):
    
    load_df = Load_Data()

    table_name = request.table_name

    if table_name == "suppliers":
        df = load_df.load("suppliers")
    if table_name == "sales_orders":
        df = load_df.load("sales_orders")
    if table_name == "inventory":
        df = load_df.load("inventory")

    return TableResponse(
        table=df.to_dict(orient="records")
    )


@router.get("/sales_orders")
def sales_dashboard():
    
    top5 = plots_data.top5_prods()

    revenue = plots_data.cat_revenue()


    return {
        "plots":{
            "top5_prods":top5.to_dict(orient="records"),
            "revenue_by_cat":revenue.to_dict(orient="records")
        }
    }

@router.get("/suppliers")
def supplier_dashboard():
    
    top5_suppliers = plots_data.supplier_plots()


    return {
        "plots":{
            "top5_suppliers":top5_suppliers.to_dict(orient="records"),
        }
    }

@router.get("/inventory")
def inventory_dashboard():
    
    inventory = plots_data.inventory_cat()


    return {
        "plots":{
            "inventory_by_cat":inventory.to_dict(orient="records"),
        }
    }

