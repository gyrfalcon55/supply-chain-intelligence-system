import pandas as pd
import sys 

from utils.exception import CustomException
from utils.logger import logging

class DataValidation:

    def validate_required_columns(df, required_cols):

        missing_cols = [
            col for col in required_cols
            if col not in df.columns
        ]

        if missing_cols:
            raise CustomException(
                f"Missing columns: {missing_cols}",
                sys
            )
        
        return True
    
    def validate_nulls(df, columns):

        null_counts = df[columns].isnull().sum()

        invalid = null_counts[null_counts > 0]

        if not invalid.empty:
            raise CustomException(
                f"Null values found:\n{invalid}",
                sys
            )
    
    def validate_dtypes(df):

        if not pd.api.types.is_datetime64_any_dtype(df['ds']):
            raise CustomException(
                "'ds' column is not datetime",
                sys
            )

        if not pd.api.types.is_numeric_dtype(df['y']):
            raise CustomException(
                "'y' column must be numeric",
                sys
            )
        
    def validate_duplicates(df):

        duplicates = df.duplicated(
            subset=['unique_id', 'ds']
        )

        if duplicates.sum() > 0:
            raise CustomException(
                f"Found {duplicates.sum()} duplicate rows",
                sys
            )


    def validate_negative_values(df):

        negatives = (df['y'] < 0).sum()

        if negatives > 0:
            raise CustomException(
                f"Found {negatives} negative demand values",
                sys
            )


    def validate_empty_df(df, df_name:str):

        if df.empty:
            raise CustomException(
                f"{df_name} is empty",
                sys
            )


    def validate_sorted_dates(df):

        for sku, group in df.groupby('unique_id'):

            if not group['ds'].is_monotonic_increasing:
                raise CustomException(
                    f"Dates not sorted for SKU {sku}",
                    sys
                )



    def validate_min_history(df, min_periods=10):

        sku_counts = (
            df.groupby('unique_id')
            .size()
        )

        invalid = sku_counts[sku_counts < min_periods]

        if not invalid.empty:
            raise CustomException(
                f"SKUs with insufficient history:\n{invalid}",
                sys
            )
























































