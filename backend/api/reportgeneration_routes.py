from fastapi import APIRouter
from backend.schemas.request import ReportGenerationRequest
from backend.pipelines.forecasting_pipeline import reports

router = APIRouter()

reports_data = reports()

@router.post("/reports")
def report_generation_route(request: ReportGenerationRequest):

    report_name = request.report_name

    if report_name == "Inventory Report":
        summary = reports_data.stock_summary()
        return {
            "stock_summary":summary
        }
    

    
    if request.report_name == "Supplier Report":

        summary = reports_data.stock_summary()

        all_suppliers = {
            label: df.to_dict(orient="records")
            for label, df in reports_data.get_suppliers_for_actionable_labels().items()
        }

        return {
            "stock_summary": summary,
            "all_suppliers": all_suppliers
        }
    if report_name == "Recommended Suppliers":
        consolidated = reports_data.consolidate_by_supplier()
        return {
            "consolidated":consolidated
        }

