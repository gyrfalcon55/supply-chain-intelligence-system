from utils.logger import logging
from utils.exception import CustomException
import sys


from sqlalchemy import text
from sqlalchemy import create_engine

import pandas as pd

from configs.config import api


DATABASE_URL = api.DB_URL

sql_engine = create_engine(DATABASE_URL)

if sql_engine:
    logging.info("Database engine created successfully")
else:
    logging.error("Database engine creation failed")



def save_to_db(df,table_name,schema_name):
    logging.info(f"Saving the {table_name} to the database for further usage")
    try:
        if not schema_name:
            raise ValueError("schema_name is empty")

        if not table_name:
            raise ValueError("table_name is empty")

        with sql_engine.begin() as conn:
                conn.execute(
                    text(
                        f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'
                    )
                )

                conn.commit()

        df.to_sql(
            table_name,
            sql_engine,
            if_exists = 'replace', 
            schema = schema_name,
            index = False
        )
        logging.info(f"Successfully saved the {table_name} to database as - '{schema_name}.{table_name}'")

    except Exception as e:
        logging.critical(f"Error while saving the {table_name} to database -- \n {str(e)}")
        raise CustomException(e,sys)


def load_from_db(query,table_name,params=None) -> pd.DataFrame :
        try: 
            logging.info(f"loading {table_name} from the database")


            with sql_engine.connect() as conn:
                    
                    df = pd.read_sql(
                        query,
                        conn,
                        params=params
                    )
            logging.info(f"Successfully loaded {table_name} from database")
            return df
        except Exception as e:
            logging.critical(f"Error while loading data from database -- \n{str(e)}")
            raise CustomException(e,sys)


def append_to_db(df,table_name,schema_name):
    logging.info(f"Appending the {table_name} to the database for further usage")
    try:
        if not schema_name:
            raise ValueError("schema_name is empty")

        if not table_name:
            raise ValueError("table_name is empty")

        with sql_engine.begin() as conn:
            conn.execute(
                text(
                    f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'
                )
            )

            conn.commit()

        df.to_sql(
            table_name,
            sql_engine,
            if_exists = 'append', 
            schema = schema_name,
            index = False
        )
        logging.info(f"Successfully appended the {table_name} to database as - '{schema_name}.{table_name}'")

    except Exception as e:
        logging.critical(f"Error while appending the {table_name} to database -- \n {str(e)}")
        raise CustomException(e,sys)