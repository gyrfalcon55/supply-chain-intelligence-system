from backend.services.db_service import Load_Data
from utils.db_crud import save_to_db

from utils.logger import logging
from utils.exception import CustomException

import pandas as pd
import sys


class ShipmentSimulator:

    def run_shipment_simulation(self, current_date: pd.Timestamp):

        """
        Shipment Lifecycle

        Pending
            ↓ (next day)
        In_Transit
            ↓ (Expected_Delivery_Date reached)
        Delivered
            ↓
        Inventory Updated
        """

        try:


            logging.info(
                "Running Shipment Simulation..."
            )

            loader = Load_Data()

            orders = loader.load("procurement").copy()
            orders["Order_Date"] = pd.to_datetime(
                orders["Order_Date"]
            )

            orders["Expected_Delivery_Date"] = pd.to_datetime(
                orders["Expected_Delivery_Date"]
            )

            orders["Actual_Delivery_Date"] = pd.to_datetime(
                orders["Actual_Delivery_Date"],
                errors="coerce"
            )

            current_date = pd.to_datetime(current_date)

            inventory = loader.load("inventory").copy()

            # =====================================================
            # Process every procurement order
            # =====================================================

            for idx, row in orders.iterrows():

                status = row["Order_Status"]

                order_date = pd.to_datetime(
                    row["Order_Date"]
                )

                expected_delivery = pd.to_datetime(
                    row["Expected_Delivery_Date"]
                )

                

                # ------------------------------------------
                # Pending → In Transit
                # ------------------------------------------

                if (
                    status == "Pending"
                    and current_date > order_date
                ):

                    orders.at[
                        idx,
                        "Order_Status"
                    ] = "In_Transit"

                # ------------------------------------------
                # In Transit → Delivered
                # ------------------------------------------

                elif (
                    status == "In_Transit"
                    and current_date >= expected_delivery
                ):

                    orders.at[
                        idx,
                        "Order_Status"
                    ] = "Delivered"

                    orders.at[
                        idx,
                        "Actual_Delivery_Date"
                    ] = current_date

                    product = row["Product_ID"]

                    qty = row["Qty_To_Order"]

                    inv_idx = inventory[
                        inventory["Product_ID"] == product
                    ].index

                    if len(inv_idx) > 0:

                        inv = inv_idx[0]

                        inventory.at[
                            inv,
                            "Current_Stock"
                        ] += qty

                        inventory.at[
                            inv,
                            "Inventory_Value"
                        ] = round(
                            inventory.at[inv, "Current_Stock"]
                            * inventory.at[inv, "Unit_Cost"],
                            2
                        )

                        inventory.at[
                            inv,
                            "Last_Updated"
                        ] = current_date

            # =====================================================
            # Save Updates
            # =====================================================

            save_to_db(
                orders,
                "procurement_orders",
                "procurements_data"
            )

            save_to_db(
                inventory,
                "inventory_data",
                "master_data"
            )

            logging.info(
                "Shipment simulation completed successfully."
            )

            return {
                "status": "Success",
                "current_date": str(current_date)
            }

        except Exception as e:

            logging.critical(str(e))

            raise CustomException(e, sys)