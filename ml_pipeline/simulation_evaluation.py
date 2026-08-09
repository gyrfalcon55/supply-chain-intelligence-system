import pandas as pd
import numpy as np
import mlflow
import os
import sys

from functools import partial
from sqlalchemy import text

import utilsforecast.losses as ufl
from utilsforecast.evaluation import evaluate

from utils.logger import logging
from utils.exception import CustomException
from backend.services.db_service import Load_Data


class SimulationEvaluation:

    # --------------------------------------------------------
    # Create Evaluation Dataset
    # --------------------------------------------------------

    def create_eval_df(self):

        logging.info(
            "Creating rolling evaluation dataset"
        )

        load_df = Load_Data()

        forecast_df = load_df.load("forecast")

        actual_df = load_df.load("simulated_sales")

        forecast_df["ds"] = (
            pd.to_datetime(
                forecast_df["ds"],
                format="mixed"
            )
        )

        actual_df["ds"] = (
            pd.to_datetime(
                actual_df["ds"],
                format="mixed"
            )
        )

        latest_week = actual_df["ds"].max()

        forecast_df = forecast_df[
            forecast_df["ds"] == latest_week
        ]

        actual_df = actual_df[
            actual_df["ds"] == latest_week
        ]




        eval_df = forecast_df.merge(

            actual_df[
                [
                    "unique_id",
                    "ds",
                    "y"
                ]
            ],

            on=[
                "unique_id",
                "ds"
            ],

            how="inner"
        )

        duplicates = eval_df.duplicated(
            subset=["unique_id", "ds"]
        ).sum()

        logging.info(
            f"Duplicate rows: {duplicates}"
        )


        if eval_df.empty:

            logging.warning(
                "No forecast has actual observations yet."
            )

            return None

        logging.info(
            f"Evaluation rows : {len(eval_df)}"
        )

        return eval_df

    # --------------------------------------------------------
    # Metric Evaluation
    # --------------------------------------------------------

    def metric_evaluation(
        self,
        train_df,
        eval_df
    ):

        forecast_col = "CrostonClassic"

        errors = (
            eval_df["y"]
            - eval_df[forecast_col]
        )

        mae = np.mean(np.abs(errors))

        rmse = np.sqrt(
            np.mean(errors ** 2)
        )

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

            train_df=train_df[
                [
                    "unique_id",
                    "ds",
                    "y"
                ]
            ]
        )

        mase = (
            mase_df
            .groupby("metric")[forecast_col]
            .mean()
            .iloc[0]
        )

        metrics = pd.Series({

            "mae": float(mae),

            "rmse": float(rmse),

            "mase": float(mase)

        })

        return metrics

    # --------------------------------------------------------
    # Save Metrics
    # --------------------------------------------------------

    def save_metrics(self, metric):

        os.makedirs(
            "artifacts/metrics",
            exist_ok=True
        )

        metrics = (
            pd.DataFrame(metric)
            .reset_index()
        )

        metrics.columns = [
            "metric",
            "score"
        ]

        metrics["created_at"] = pd.Timestamp.now()

        metrics.to_csv(
            "artifacts/metrics/simulation_metrics.csv",
            mode="a",
            index=False,
            header=not os.path.exists(
                "artifacts/metrics/simulation_metrics.csv"
            )
        )

    # --------------------------------------------------------
    # Main
    # --------------------------------------------------------

    def run_evaluation(
        self
    ):

        logging.info(
            "Running Simulation Evaluation"
        )

        eval_df = self.create_eval_df()

        if eval_df is None:

            logging.info(
                "Skipping evaluation because no matching forecast horizon exists."
            )

            return None
        
        load_df = Load_Data()
        train_df = load_df.load("simulated_sales")

        metrics = self.metric_evaluation(
            train_df,
            eval_df
        )

        self.save_metrics(metrics)

        logging.info(
            "Simulation evaluation completed."
        )

        return metrics