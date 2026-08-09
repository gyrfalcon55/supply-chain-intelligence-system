import pandas as pd
from utils.logger import logging
from utils.exception import CustomException
import numpy as np

from sqlalchemy import text
from configs.config import load_config

from functools import partial

import utilsforecast.losses as ufl
from utilsforecast.evaluation import evaluate

import mlflow
import sys
import os

from utils.db_crud import save_to_db, load_from_db


from utils.data_validation import DataValidation as dv

class ModelEvaluation:

    def __init__(self):

        logging.info("loading config parameters for model evaluation")

        config = load_config()
        
        self.evaluation_schema = config['evaluation_schema']['schema_name']
        self.evaluation_test = config['evaluation_schema']['test_data']
        self.evaluation_train = config['evaluation_schema']['train_data']

        self.forecasting_schema = config['forecasting']['schema_name']
        self.forecasting_data = config['forecasting']['table_name']

        self.required_cols = ['unique_id','ds','y']

    def load_data(self,table_name,schema_name):

        query = text(f'''
                        select * from {schema_name}.{table_name};
                    ''')

        df = load_from_db(query, table_name)

        dv.validate_empty_df(df,table_name)


        return df


    def create_eval_df(self,test_data,forecasted_data):
        '''
        'eval_df' it is made by merging model's forecasted_data and test_data
        This 'eval_df' is used to measure the metrics like mae, rmse, smape
        '''

        try:
            logging.info("creating 'eval_df' by merging test_data and model's forecasted data ")
            
            if test_data.empty:
                raise CustomException("test_df dataframe is empty",sys)
            if forecasted_data.empty:
                raise CustomException("forecasted_df dataframe is empty",sys)

            logging.info(
                f"Test data dates: "
                f"{test_data['ds'].min()} -> "
                f"{test_data['ds'].max()}"
            )

            logging.info(
                f"Forecast data dates: "
                f"{forecasted_data['ds'].min()} -> "
                f"{forecasted_data['ds'].max()}"
            )



            
            eval_df = test_data.merge(
                forecasted_data,
                on = ['unique_id','ds'], 
                how = 'left'
            )
            if eval_df.isnull().sum().sum() > 0:
                raise CustomException("Null values found after merging forecasts with test data",sys)

            dv.validate_duplicates(eval_df)

            dv.validate_nulls(eval_df,self.required_cols)

            return eval_df
        
        except Exception as e:
            logging.critical(f"Error whie creating 'eval_df' -- \n {str(e)}")
            raise CustomException(e,sys)
    
    def metric_evaluation(self, train_df, eval_df, run_id):
        """
        Compute global MAE, RMSE, SMAPE manually and MASE using utilsforecast.
        """

        try:

            logging.info("Computing evaluation metrics")

            if train_df.empty:
                raise CustomException("train_df dataframe is empty", sys)

            if eval_df.empty:
                raise CustomException("eval_df dataframe is empty", sys)

            # ---------------------------------------------------
            # Prepare Data
            # ---------------------------------------------------

            train_df = train_df[["unique_id", "ds", "y"]]

            eval_df = eval_df.drop(
                columns=["zero_demand_ratio"],
                errors="ignore"
            )

            forecast_col = "CrostonClassic"

            # ---------------------------------------------------
            # Global Metrics
            # ---------------------------------------------------

            errors = eval_df["y"] - eval_df[forecast_col]

            mae = np.mean(np.abs(errors))

            rmse = np.sqrt(np.mean(errors ** 2))



            # ---------------------------------------------------
            # MASE
            # ---------------------------------------------------

            mase_df = evaluate(
                df=eval_df[
                    [
                        "unique_id",
                        "ds",
                        "y",
                        forecast_col
                    ]
                ],

                metrics=[
                    partial(
                        ufl.mase,
                        seasonality=1
                    )
                ],

                train_df=train_df
            )

            mase = (
                mase_df
                .groupby("metric")[forecast_col]
                .mean()
                .iloc[0]
            )

            # ---------------------------------------------------
            # Summary
            # ---------------------------------------------------

            summary_metrics = pd.Series(
                {
                    "mae": float(mae),
                    "rmse": float(rmse),
                    "mase": float(mase)
                }
            )

            logging.info("\nEvaluation Metrics")
            logging.info("------------------------------")
            logging.info(f"MAE   : {mae:.4f}")
            logging.info(f"RMSE  : {rmse:.4f}")
            logging.info(f"MASE  : {mase:.4f}")

            # ---------------------------------------------------
            # MLflow
            # ---------------------------------------------------

            for metric_name, metric_value in summary_metrics.items():

                mlflow.log_metric(
                    metric_name,
                    float(metric_value)
                )

            return summary_metrics

        except Exception as e:

            logging.critical(
                f"Error while computing metrics\n{str(e)}"
            )

            raise CustomException(e, sys)
    
    def save_metrics(self, metric):

        os.makedirs('artifacts/metrics', exist_ok=True)

        metrics = pd.DataFrame(metric).reset_index()
        metrics.columns = ['metric', 'score']

        metrics['created_at'] = pd.Timestamp.now()

        metrics.to_csv(
            'artifacts/metrics/metrics.csv',
            mode='a',
            index=False,
            header=not os.path.exists('artifacts/metrics/metrics.csv')
        )
    
    def save_df(self,df,table_name,schema_name):

        save_to_db(df,table_name,schema_name)

    def run_evaluation(self, run_id):
        try:
            logging.info("\n---------------------------Running evaluation.py---------------------------\n")
            test_df = self.load_data(self.evaluation_test,self.evaluation_schema)

            train_df = self.load_data(self.evaluation_train,self.evaluation_schema)
            
            forecast_df = self.load_data(self.forecasting_data,self.forecasting_schema)

            eval_df = self.create_eval_df(test_df,forecast_df)

            self.save_df(eval_df,"merged_data",'evaluation_data')

            metrics = self.metric_evaluation(train_df,eval_df,run_id)

            self.save_metrics(metrics)
            logging.info("\n---------------------------Completed evaluation.py---------------------------\n")
            return metrics
        except Exception as e:
            logging.critical(f"Error while running evaluaiton.py -- \n{str(e)}")
            raise CustomException(e,sys)



