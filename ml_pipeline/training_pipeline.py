import pandas as pd
from sqlalchemy import text 

from utils.db_crud import save_to_db, load_from_db
from sqlalchemy import text

from statsforecast import StatsForecast
from statsforecast.models import CrostonClassic

from utils.logger import logging
from utils.exception import CustomException
import sys

from configs.config import load_config
import pickle
import os

from utils.data_validation import DataValidation as dv
from ml_pipeline.simulation_evaluation import SimulationEvaluation
import mlflow

from dotenv import load_dotenv
from utils.db_crud import append_to_db
from ml_pipeline.evaluation import ModelEvaluation

load_dotenv()
MODEL_DB_URL = os.getenv('DB_URL')

class TrainingPipeline:

    def __init__(self):
        config = load_config()
        self.processed_schema = config['processed_schema']['schema_name']
        self.processed_data = config['processed_schema']['table_name']

        self.evaluation_schema = config['evaluation_schema']['schema_name']
        self.evaluation_test = config['evaluation_schema']['test_data']
        self.evaluation_train = config['evaluation_schema']['train_data']


        self.forecasting_schema = config['forecasting']['schema_name']
        self.forecasting_table = config['forecasting']['table_name']

        self.freq = config['forecasting']['frequency']
        self.horizon = config['forecasting']['horizon']

        self.required_cols = ['unique_id','ds','y']

        self.model_path = config['artifacts']['model_dir']

    def load_data(self, table_name, schema_name) -> pd.DataFrame:

        query = text(f'''
                        select * from {schema_name}.{table_name};
                    ''')

        df = load_from_db(query,table_name)

        dv.validate_empty_df(df,'df')
        dv.validate_required_columns(df,self.required_cols)

        dv.validate_sorted_dates(df)
        return df
        
    
    def split_data(self, df:pd.DataFrame,horizon) -> pd.DataFrame:
        f'''
        As we know the date for TimeSeries forecasting need to be in order. 
        So while splitting the data into train and test we need to follow the same 
        process.

        - We need to keep a threshold, in this case i'm using '{horizon} weeks'
        - '{horizon} weeks' data for each sku will be used as test data
        and the remaining is used to train the model.
        '''

        try:
            logging.info(
                "Splitting train and test data per SKU"
            )

            train_list = []
            test_list = []
            dv.validate_min_history(df)

            for sku, group in df.groupby('unique_id'):

                group = group.sort_values('ds')

                test = group.tail(horizon)

                train = group.iloc[:-horizon]

                train_list.append(train)

                test_list.append(test)

            train_data = pd.concat(train_list)

            dv.validate_empty_df(train_data,'train_data')
            dv.validate_sorted_dates(train_data)
            dv.validate_negative_values(train_data)


            test_data = pd.concat(test_list)

            dv.validate_empty_df(test_data,'test_data')
            dv.validate_sorted_dates(test_data)
            dv.validate_negative_values(test_data)
            return train_data, test_data

        except Exception as e:

            logging.critical(
                f"Error while splitting data \n {str(e)}"
            )

            raise CustomException(e, sys)
        
    
    def train_model(self,train_data):
        try:
            logging.info("Training the CrostonClassic model on the dataset ")
            mlflow.set_tracking_uri("http://127.0.0.1:5000")
            mlflow.set_experiment("supply_chain_forecasting")
            if mlflow.active_run():
                logging.warning(
                    "Active MLflow run detected."
                )
            with mlflow.start_run() as run:

                self.run_id = str(run.info.run_id)

                models = [CrostonClassic()]

                sf = StatsForecast(
                    models=models,
                    freq=self.freq
                )

                sf.fit(df=train_data)

                self.save_model(sf)

                mlflow.sklearn.log_model(
                    sk_model=sf,
                    name="model",
                    registered_model_name="sales_forecasting_model"
                )

                mlflow.log_param("model", "CrostonClassic")
                mlflow.log_param("frequency", self.freq)
                mlflow.log_param("horizon", self.horizon)

                logging.info(f"Mlflow run_id : {str(run.info.run_id)}")

                return sf
        
        except Exception as e:
            logging.critical(f"Error while training the model -- \n{str(e)}")
            raise CustomException(e,sys)

    def predict_output(self,model,horizon):
        
        try:
            logging.info(f"forecasting {horizon}-weeks data using the trained model")
            result = model.predict(h=horizon)

            return result
        except Exception as e:
            logging.critical(f"Error while forecasting output -- \n{str(e)}")
            raise CustomException(e,sys)


    def save_model(self, model):

        os.makedirs(self.model_path, exist_ok=True)

        model_file = f"Model-{self.run_id}.pkl"

        full_path = os.path.join(
            self.model_path,
            model_file
        )

        with open(full_path, 'wb') as file:
            pickle.dump(model, file)

        return full_path
        
    def run_training_pipeline(self, df, simulation):

        train_data, test_data = self.split_data(df, self.horizon)

        trained_model = self.train_model(train_data)

        forecast = self.predict_output(trained_model, self.horizon)

        append_to_db(forecast,"forecast_data","master_data")




        if not simulation:

            self.save_df(
                test_data,
                self.evaluation_test,
                self.evaluation_schema
            )

            self.save_df(
                train_data,
                self.evaluation_train,
                self.evaluation_schema
            )

            model_eval = ModelEvaluation()

            metrics = model_eval.run_evaluation(self.run_id)

            return {
                "run_id": self.run_id,
                "metrics": metrics
            }

        return {
            "run_id": self.run_id,
            "metrics": None
        }

if __name__=="__main__":

    pipe = TrainingPipeline()
    res = pipe.run_training_pipeline()