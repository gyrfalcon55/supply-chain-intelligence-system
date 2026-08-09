from fastapi import APIRouter

from backend.services.simulation_services.sales_service import SalesSimulator
from backend.services.simulation_services.planning_service import PlanningService
from backend.services.simulation_services.shipment_service import ShipmentSimulator

import pandas as pd
router = APIRouter()


@router.post("/simulation/run_day")
def run_day():

    simulator = SalesSimulator()

    result = simulator.run_sales_simulation()

    # Shipment progresses every simulated day
    shipment_simulator = ShipmentSimulator()

    current_date = pd.to_datetime(result["current_date"])

    shipment_simulator.run_shipment_simulation(current_date)

    # Weekly planning
    if result["planning_due"]:

        planning_result = PlanningService().run_planning_pipeline()

        result["planning_date"] = str(
            planning_result["planning_date"]
        )

    result["current_date"] = result["current_date"].strftime("%Y-%m-%d")

    return result