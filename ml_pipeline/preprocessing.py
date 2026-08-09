import pandas as pd
from utils.db_crud import load_from_db,save_to_db
from utils.exception import CustomException
from sqlalchemy import text
import sys

from utils.logger import logging
from configs.config import load_config

from utils.data_validation import DataValidation as dv


class PreprocessingPipeline:


    def __init__(self):
        config = load_config()
        self.processed_schema = config['processed_schema']['schema_name']
        self.processed_data = config['processed_schema']['table_name']

        self.required_cols = ['unique_id','ds','y']

    def load_data(self,table_name,schema_name) -> pd.DataFrame:

        query = text(f'select "unique_id","ds","y" from {schema_name}.{table_name};')

        df = load_from_db(query,table_name)

        dv.validate_required_columns(df,self.required_cols)

        return df
    

    def fill_missing_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensures every SKU has a continuous weekly time series ending at the
        latest date present in the entire dataset.

        Missing weeks are filled with zero demand.
        """

        try:

            logging.info(
                "Filling missing weekly dates and aligning all SKUs to a common end date."
            )

            result = []

            logging.info(
                "Length of dataset before filling dates: %s",
                len(df)
            )

            # Convert to datetime
            df["ds"] = pd.to_datetime(df["ds"])

            # Global last historical week
            global_end = df["ds"].max()

            logging.info(
                "Global end date: %s",
                global_end.date()
            )

            for product, group in df.groupby("unique_id"):

                group = group.sort_values("ds")

                group = group.set_index("ds")

                full_range = pd.date_range(
                    start=group.index.min(),
                    end=global_end,
                    freq="W"
                )

                group = (
                    group["y"]
                    .reindex(full_range, fill_value=0)
                    .to_frame()
                )

                group.index.name = "ds"

                group["unique_id"] = product

                group = group.reset_index()

                result.append(group)

            df = pd.concat(result, ignore_index=True)

            df = df[
                [
                    "unique_id",
                    "ds",
                    "y"
                ]
            ]

            dv.validate_duplicates(df)

            dv.validate_nulls(df, self.required_cols)

            dv.validate_sorted_dates(df)

            dv.validate_negative_values(df)

            logging.info(
                "Length of dataset after filling dates: %s",
                len(df)
            )

            return df

        except Exception as e:

            logging.critical(
                f"Error while filling missing dates\n{str(e)}"
            )

            raise CustomException(e, sys)
    

    def save_df(self,df,table_name,schema_name):

        save_to_db(df,table_name,schema_name)
        


    def run_preprocessing_pipeline(self):
        try:
            logging.info("\n---------------------------Running preprocessing.py---------------------------\n")

            df = self.load_data(self.processed_data,self.processed_schema)

            df = self.fill_missing_dates(df)

            self.save_df(df,self.processed_data,self.processed_schema)

            logging.info("\n---------------------------Completed preprocessing.py---------------------------\n")
            
            return df 
        
        except Exception as e:
            logging.critical("Error while running the preprocessing pipeline")
            raise CustomException(e,sys)





