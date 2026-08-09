from utils.db_crud import append_to_db,save_to_db
import pandas as pd

from utils.logger import logging
from utils.exception import CustomException
import sys

from backend.services.db_service import Load_Data
from ml_pipeline.ML_Orchestration import Ml_Pipeline
from backend.pipelines.forecasting_pipeline import reports

from ml_pipeline.simulation_evaluation import SimulationEvaluation

class PlanningService:

    def append_to_weekly_sales(self, weekly_sales):
    
        append_to_db(weekly_sales,'simulated_sales','simulation_data') 


    def aggregate_daily_to_weekly(self) -> pd.DataFrame:
        """
        Aggregate one week of simulated daily sales into weekly demand.

        Returns
        -------
        unique_id
        ds
        y
        """

        try:

            logging.info("Aggregating simulated daily sales to weekly demand")
            load_df = Load_Data()
            self.daily_sales_table = load_df.load("simulated_daily_sales")

            latest_week = self.daily_sales_table["Sales_Date"].max()

            week_start = latest_week - pd.Timedelta(days=6)

            week_sales = self.daily_sales_table[
                (self.daily_sales_table["Sales_Date"] >= week_start) &
                (self.daily_sales_table["Sales_Date"] <= latest_week)
            ]

            weekly_sales = (
                week_sales
                .groupby("Product_ID", as_index=False)["Sales_qty"]
                .sum()
                .rename(
                    columns={
                        "Product_ID": "unique_id",
                        "Sales_qty": "y"
                    }
                )
            )

            weekly_sales["ds"] = latest_week

            weekly_sales = weekly_sales[
                ["unique_id", "ds", "y"]
            ]

            logging.info("Weekly sales aggregation completed")

            return weekly_sales

        except Exception as e:

            logging.critical(
                f"Error while aggregating daily sales\n{str(e)}"
            )

            raise CustomException(e, sys)

    def update_zero_demand_ratio(self):
        """
        Recompute zero-demand ratio using the complete
        simulation history.
        """

        try:

            logging.info("Updating zero-demand ratio")

            # Reload latest simulation history
            load_df = Load_Data()
            sales = load_df.load("simulated_sales")

            zero_ratio = (
                sales.groupby("unique_id")["y"]
                .apply(lambda x: (x == 0).mean())
                .reset_index(name="zero_demand_ratio")
            )

            sales = (
                sales.drop(columns=["zero_demand_ratio"], errors="ignore")
                .merge(
                    zero_ratio,
                    on="unique_id",
                    how="left"
                )
            )

            save_to_db(
                sales,
                "simulated_sales",
                "simulation_data"
            )

            logging.info("Zero-demand ratio updated successfully")

        except Exception as e:

            logging.critical(str(e))

            raise CustomException(e, sys)

    def update_last_planning_date(self, planning_date):
        load_df = Load_Data()

        inventory = load_df.load("inventory")

        inventory["Last_Planning_Date"] = planning_date

        save_to_db(
            inventory,
            "inventory_data",
            "master_data"
        )


    def run_planning_pipeline(self):

        try:

            logging.info("Planning pipeline started")

            

            # ----------------------------
            # 1. Aggregate last 7 days
            # ----------------------------
            weekly_sales = self.aggregate_daily_to_weekly()

            self.append_to_weekly_sales(weekly_sales)

            simulation_eval = SimulationEvaluation()
            
            simulation_eval.run_evaluation()
            # ----------------------------
            # 2. Update intermittent demand statistics
            # ----------------------------
            self.update_zero_demand_ratio()

            # ----------------------------
            # 3. Retrain forecasting model
            # ----------------------------
            ml_pipeline = Ml_Pipeline()

            ml_pipeline.run_simulation_pipeline()

            # ----------------------------
            # 4. Refresh inventory labels
            # ----------------------------
            label = reports()

            label.label_data()

            # ----------------------------
            # 5. Planning date
            # ----------------------------
            planning_date = weekly_sales["ds"].max()

            self.update_last_planning_date(planning_date)

            logging.info(f"Planning completed for {planning_date}")

            return {
                "planning_date": pd.to_datetime(planning_date),
                "planning_due": True
            }

        except Exception as e:

            logging.critical(str(e))

            raise CustomException(e, sys)


        except CustomException as e:
            logging.critical(
                f"Error while running planning pipeline\n{str(e)}"
            )














