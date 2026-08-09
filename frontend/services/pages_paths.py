from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

FRONTEND_COMPONENTS_PATH = BASE_DIR / "components"

AGENT_PAGE_PATH = (
    FRONTEND_COMPONENTS_PATH
    / "chatbot"
    / "chatbot.py"
)

TABLE_VIEW_PAGE_PATH = (
    FRONTEND_COMPONENTS_PATH
    / "visuals"
    / "table_view.py"
)

INVENTORY_SUPPLIER_REPORT_PAGE_PATH = (
    FRONTEND_COMPONENTS_PATH
    / "inventory_and_suppliers"
    / "inventory_and_supplier_report.py"
)

PROCUREMENT_ORDERS_PAGE_PATH = (
    FRONTEND_COMPONENTS_PATH
    / "procurements"
    / "procurement_orders.py"
)

SIMULATION_PAGE_PATH = (
    FRONTEND_COMPONENTS_PATH
    / "simulation"
    / "simulation_ui.py"
)

ML_PIPELINE_PAGE_PATH = (
    FRONTEND_COMPONENTS_PATH
    / "MachineLearning"
    / "ml_pipeline.py"
)
