from backend.services.db_service import Load_Data
import numpy as np
import pandas as pd

from utils.logger import logging
from utils.exception import CustomException
import sys

from ml_pipeline.preprocessing import PreprocessingPipeline
from ml_pipeline.ML_Orchestration import Ml_Pipeline
from backend.services.simulation_services.planning_service import PlanningService
from backend.pipelines.forecasting_pipeline import reports





from utils.db_crud import append_to_db,save_to_db

class SalesSimulator:

    def __init__(self, random_state: int = 42):

        self.rng = np.random.default_rng(random_state)
        load_df = Load_Data()
        self.inventory = load_df.load("inventory")
        self.forecast = load_df.load("forecast")
        self.sales_table = load_df.load("simulated_sales")

        last_date = self.inventory["Last_Updated"].max()
        self.current_date = pd.to_datetime(last_date) + pd.Timedelta(days=1)
    

    def prods_tables(self):
        grouped_sales = self.sales_table[['unique_id','zero_demand_ratio']].groupby('unique_id').mean().reset_index()
        grouped_sales = grouped_sales.rename(columns={"unique_id":"Product_ID"})

        prods = self.inventory.merge(right=grouped_sales,on='Product_ID',how='left')[['Product_ID','zero_demand_ratio','Current_Stock']]

        forecast = self.forecast.rename(columns={"unique_id":"Product_ID","CrostonClassic":"forecast"})

        products = prods.merge(on='Product_ID',right=forecast,how='left')[['Product_ID','zero_demand_ratio','Current_Stock','forecast']]

        return products


    def generate_sales(self) -> pd.DataFrame:
        """
        Generate one day's simulated sales for each SKU.

        Required Columns
        ----------------
        Product_ID
        Current_Stock
        forecast          # Weekly Croston forecast
        zero_demand_ratio

        Returns
        -------
        Sales_Date
        Product_ID
        Opening
        Forecast
        Demand
        Sales_qty
        Lost_sales
        Closing
        """

        try:

            logging.info("Generating simulated daily sales")

            products = self.prods_tables()

            sales = []

            for _, row in products.iterrows():

                sku = row["Product_ID"]

                stock = int(row["Current_Stock"])

                weekly_forecast = max(float(row["forecast"]), 0)

                zero_ratio = float(row["zero_demand_ratio"])

                # Convert weekly forecast to expected daily demand
                daily_forecast = weekly_forecast / 7.0

                # -----------------------------
                # Generate Demand
                # -----------------------------

                if stock <= 0:

                    demand = 0

                elif self.rng.random() < zero_ratio:

                    # Intermittent no-demand day
                    demand = 0

                else:

                    demand = self.rng.poisson(
                        lam=max(daily_forecast, 0.01)
                    )

                # -----------------------------
                # Inventory constraint
                # -----------------------------

                sales_qty = min(demand, stock)

                lost_sales = max(0, demand - sales_qty)

                closing_stock = stock - sales_qty

                sales.append(
                    {
                        "Sales_Date": self.current_date,
                        "Product_ID": sku,
                        "Opening": stock,
                        "Forecast": round(weekly_forecast, 2),
                        "Demand": int(demand),
                        "Sales_qty": int(sales_qty),
                        "Lost_sales": int(lost_sales),
                        "Closing": int(closing_stock)
                    }
                )

            logging.info("Daily sales generated successfully")

            return pd.DataFrame(sales)

        except Exception as e:

            logging.critical(
                f"Error while generating simulated sales\n{str(e)}"
            )

            raise CustomException(e, sys)

      

    def append_daily_sales(self,daily_sales):

        append_to_db(daily_sales,'simulated_daily_sales','simulation_data')


    def update_inventory(self, daily_sales: pd.DataFrame):

        """
        Update inventory after one day of simulated sales.
        """

        try:

            updated_inventory = self.inventory.merge(
                daily_sales[
                    ["Product_ID", "Closing", "Sales_Date"]
                ],
                on="Product_ID",
                how="left"
            )

            updated_inventory["Current_Stock"] = updated_inventory["Closing"]

            updated_inventory["Last_Updated"] = updated_inventory["Sales_Date"]

            updated_inventory["Inventory_Value"] = round(
                updated_inventory["Unit_Cost"]
                * updated_inventory["Current_Stock"],2
            )


            updated_inventory = updated_inventory.drop(
                columns=["Closing", "Sales_Date"]
            )

            self.inventory = updated_inventory

            return updated_inventory

        except Exception as e:

            logging.critical(
                f"Error while updating inventory\n{str(e)}"
            )

            raise CustomException(e, sys)
    

    def run_sales_simulation(self):

        # -------------------------
        # Simulate today's sales
        # -------------------------
        today_sales = self.generate_sales()

        self.append_daily_sales(today_sales)

        updated_inventory = self.update_inventory(today_sales)

        save_to_db(
            updated_inventory,
            "inventory_data",
            "master_data"
        )

        self.inventory = updated_inventory

        # -------------------------
        # Check planning cycle
        # -------------------------
        last_planning_date = updated_inventory[
            "Last_Planning_Date"
        ].max()

        planning_day = (
            self.current_date - last_planning_date
        ).days

        planning_due = planning_day >= 7

        # -------------------------
        # Return status
        # -------------------------
        return {
            "status": "Simulation Completed",
            "current_date": self.current_date,
            "planning_due": planning_due,
            "planning_day": planning_day,
            "days_remaining": max(0, 7 - planning_day)
        }



