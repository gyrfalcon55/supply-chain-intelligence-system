from utils.db_crud import load_from_db


class Load_Data:

    TABLES = {
        "forecast": (
            "select * from forecast_data.forecast_sales_orders;",
            "forecast_table",
        ),
        "inventory": (
            "select * from master_data.inventory_data;",
            "inventory_table",
        ),
        "suppliers": (
            "select * from raw_data.suppliers;",
            "supplier_table",
        ),
        "procurement": (
            "select * from procurements_data.procurement_orders;",
            "procurement_table",
        ),
        "sales_orders": (
            "select * from raw_data.sales_orders;",
            "sales_orders",
        ),
        "products": (
            "select * from raw_data.products;",
            "products_table",
        ),
        "labeled_inventory": (
            "select * from master_data.labeled_inventory_data;",
            "labeled_inventory",
        ),
        "processed_sales": (
            "select * from processed_data.processed_sales_orders;",
            "processed_sales",
        ),
        "simulated_daily_sales": (
            "select * from simulation_data.simulated_daily_sales;",
            "simulated_daily_sales_table",
        ),
        "simulated_sales": (
            "select * from simulation_data.simulated_sales;",
            "simulated_sales_table",
        ),
    }

    def load(self, table_name: str):

        if table_name not in self.TABLES:
            raise ValueError(f"Unknown table: {table_name}")

        query, log_name = self.TABLES[table_name]

        return load_from_db(query, log_name)