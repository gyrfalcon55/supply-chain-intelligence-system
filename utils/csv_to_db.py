import pandas as pd
from utils.db_crud import save_to_db

sales_orders = pd.read_csv(r"D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai\data\raw\sales_orders.csv")
save_to_db(sales_orders,'sales_orders','raw_data')


suppliers = pd.read_csv(r"D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai\data\raw\supplier_master.csv")
save_to_db(suppliers,'suppliers','raw_data')

products = pd.read_csv(r"D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai\data\raw\product_master.csv")
save_to_db(products,'products','raw_data')

procurement_orders = pd.read_csv(r"D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai\data\raw\procurement_orders.csv")
save_to_db(procurement_orders,'procurement_orders','raw_data')

customers = pd.read_csv(r"D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai\data\raw\customer_master.csv")
save_to_db(customers,'customers','raw_data')


inventory_data = pd.read_csv(r"D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai\data\raw\inventory_master.csv")
save_to_db(inventory_data,'inventory_data','master_data')

print("tables copied successfully to the 'raw_data' schema!")