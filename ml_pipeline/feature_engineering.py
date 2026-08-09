import pandas as pd
from utils.db_crud import load_from_db,save_to_db
from utils.exception import CustomException
from sqlalchemy import text
import sys

from utils.logger import logging
from configs.config import load_config

from utils.data_validation import DataValidation as dv
from backend.services.db_service import Load_Data


class FeatureEngineeringPipeline:

    def __init__(self):
        config = load_config()
        load_df = Load_Data()

        self.raw_schema = config['raw_schema']['schema_name']
        self.raw_data = load_df.load("sales_orders")

        self.processed_schema = config['processed_schema']['schema_name']
        self.processed_data = config['processed_schema']['table_name']

        self.cols = ['Product_ID','Order_Date','Order_Quantity']

    def load_data(self,table_name,schema_name) -> pd.DataFrame:

        query = text(f'select "Product_ID","Order_Date","Order_Quantity" from {schema_name}.{table_name};')

        df = load_from_db(query,table_name)

        dv.validate_empty_df(df, table_name)

        dv.validate_required_columns(df,self.cols)

        dv.validate_nulls(df,self.cols)

        return df

    
    def convert_daily_to_weekly(self,df):

        """
        As the daily granuality is very sensitive and very noise, 
        so we are converting the daily sales dataset to weekly aggregated data. 
        This helps the model to understand the spikes better and reduces noise
        """
        
        try:
            logging.info("Converting 'Order_Date' column to datatime type")
            
            df['Order_Date'] = pd.to_datetime(df['Order_Date'])
            
            logging.info("Aggregating Daily data as Weekly data")
            df = (
                df.groupby(
                ['Product_ID',pd.Grouper(key='Order_Date',freq='W')]
                )['Order_Quantity']
                .sum()
                .reset_index()
            )
            return df
        except Exception as e:
            logging.critical("Error while aggregating the data from daily frequency to weekly frequency")
            raise CustomException(e,sys)


    def change_column_names(self,df):
        """
        Croston model doesn't need any extra features like lags,rolling etc....
        These models just need the data to be in correct format and takes only three columns as 
        inputs - (
            'ds' - 'Date_Column'
            'y' - 'Output'
            'unique_id' - 'either product_id or something unique'
        )
        """
        try:

            dv.validate_nulls(df,self.cols)


            logging.info("Converting column names based on the croston model")
            df = df.rename(columns={
                'Product_ID': 'unique_id',
                'Order_Date': 'ds',
                'Order_Quantity': 'y'
            })

            new_cols = ['unique_id','ds','y']
            dv.validate_duplicates(df)
            dv.validate_dtypes(df)
            dv.validate_required_columns(df,new_cols)
            return df
        except Exception as e:
            logging.critical(f"Error while changing column names \n {str(e)}")
            raise CustomException(e,sys)

    def save_df(self,df,table_name,schema_name):

        save_to_db(df,table_name,schema_name)


    def run_featureengineering_pipeline(self):

        try:
            logging.info("\n---------------------------Running feature_engineering.py---------------------------\n")
            df = self.load_data(self.raw_data,self.raw_schema)

            df = self.convert_daily_to_weekly(df)

            df = self.change_column_names(df)

            self.save_df(df,self.processed_data,self.processed_schema)

            logging.info("\n---------------------------Completed feature_engineering.py---------------------------\n")
            return df

        except Exception as e:
            logging.critical(f"Error while running feature_engineering.py -- \n{str(e)}")
            raise CustomException(e,sys)


    

    





    