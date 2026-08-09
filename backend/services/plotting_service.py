import streamlit as st
from backend.services.db_service import Load_Data


class Visualizations_Data:

    def top5_prods(self):

        load_df = Load_Data()
        self.sales_orders = load_df.load("sales_orders")
        self.products = load_df.load("products")

        order_qty_by_product = self.sales_orders[['Product_ID','Order_Quantity']].groupby(['Product_ID']).sum()

        self.order_qty = (
            order_qty_by_product.merge(self.products,on=self.products['Product_ID'],how='right')
            [['Product_ID','SKU','Product_Name','Category','Subcategory','Order_Quantity']]
            )

        top_5_prods = self.order_qty.sort_values(by=['Order_Quantity'],ascending=False).head()
        return top_5_prods

    def inventory_cat(self):

        load_df = Load_Data()
        self.inventory = load_df.load("labeled_inventory")

        self.inventory_by_cat  = self.inventory[['stockout_label','unique_id']].groupby(by=['stockout_label'])['unique_id'].count().reset_index()

        return self.inventory_by_cat

    def cat_revenue(self):

        load_df = Load_Data()
        self.sales_orders = load_df.load("sales_orders")
        sales_agg = self.sales_orders.groupby('Product_ID')['Order_Total'].sum().reset_index()
        revenue = self.order_qty.merge(sales_agg,on='Product_ID',how='left')
        revenue['Order_Total'] = revenue['Order_Total'].astype(int)
        revenue_by_cat = revenue[['Category','Order_Total']].groupby(by='Category').sum().reset_index()

        return revenue_by_cat


    
    def supplier_plots(self):

        load_df = Load_Data()
        suppliers = load_df.load("suppliers")

        self.top5_suppliers = (
            suppliers[suppliers["Is_Preferred_Supplier"] == 1]
            .sort_values(by="On_Time_Delivery_Rate", ascending=False)
            [["Supplier_Name", "On_Time_Delivery_Rate"]]
        )

        return self.top5_suppliers.head()
       


plots_data = Visualizations_Data()