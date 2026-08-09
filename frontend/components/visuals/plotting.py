import streamlit as st

import plotly.express as px



class Visualizations:

    def top5_prods(self,data):


        fig = px.bar(
            data,
            x = "Product_Name",
            y = "Order_Quantity",
            title="Top_5 products by Order_Qunatity",
            color_discrete_sequence=px.colors.qualitative.Pastel2,
            color="Product_Name",
            text_auto=True
        )

        st.plotly_chart(fig,width='stretch')

    def ineventory_cat(self,data):

        fig = px.bar(
            data,
            x = "stockout_label",
            y = "unique_id",
            title="Inventory",
            color="stockout_label",
            color_discrete_sequence=["crimson","orange","goldenrod","forestgreen"],
            text_auto=True
        )

        st.plotly_chart(fig,width='stretch')



    def cat_revenue(self,data):
        
        fig = px.bar(
            data,
            title="Total Revenue by Each Category",
            x="Order_Total",
            y="Category",
            color="Category",
            color_discrete_sequence=px.colors.qualitative.Set3,
            orientation='h',
            text_auto=True
        )

        st.plotly_chart(fig,width='stretch')
    

    
    def supplier_plot(self,data):

        fig = px.bar(
            data,
            title="Top 5 Suppliers by Delivery Rate and Preference",
            x="Supplier_Name",
            y="On_Time_Delivery_Rate",
            color="Supplier_Name",
            color_discrete_sequence=px.colors.qualitative.Prism,
            text_auto=True
        )
        
        st.plotly_chart(fig,width='stretch')

        


plots = Visualizations()