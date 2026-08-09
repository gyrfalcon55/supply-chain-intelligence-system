from ml_pipeline.preprocessing import PreprocessingPipeline
from ml_pipeline.feature_engineering import FeatureEngineeringPipeline
from ml_pipeline.training_pipeline import TrainingPipeline

from backend.services.db_service import Load_Data

from utils.logger import logging

import pandas as pd


class Ml_Pipeline:

    def __init__(self):

        self.preprocessing = PreprocessingPipeline()
        self.feature_engineering = FeatureEngineeringPipeline()
        self.training = TrainingPipeline()

        self.loader = Load_Data()

    # ==========================================================
    # First Time Project Initialization
    # ==========================================================

    def run_initial_pipeline(self, job):

        """
        Executes only once.

        Raw Historical Data
                ↓
        Feature Engineering
                ↓
        Preprocessing
                ↓
        Training
                ↓
        Forecast
        """

        job["progress"] = 10
        job["status"] = "Feature Engineering"

        self.feature_engineering.run_featureengineering_pipeline()

        job["progress"] = 35
        job["status"] = "Preprocessing"

        self.preprocessing.run_preprocessing_pipeline()

        train_df = self.loader.load("processed_sales")

        return self.__train_model(
            train_df=train_df,
            job=job
        )

    # ==========================================================
    # Weekly Retraining During Simulation
    # ==========================================================

    def run_simulation_pipeline(self, job=None):

        """
        Executes every 7 simulated days.

        Simulated Weekly Sales
                ↓
        Training
                ↓
        Forecast
        """

        train_df = self.loader.load("simulated_sales")

        return self.__train_model(
            train_df=train_df,
            job=job,
            simulation=True
        )

    # ==========================================================
    # Common Training Logic
    # ==========================================================

    def __train_model(self, train_df, job=None, simulation=False):

        if job is not None:

            job["progress"] = 60
            job["status"] = "Training"

        result = self.training.run_training_pipeline(
            train_df,
            simulation
        )

        # -----------------------------
        # Historical pipeline
        # -----------------------------
        if not simulation:

            metric = result["metrics"]

            metrics = (
                pd.DataFrame(metric)
                .reset_index()
            )

            metrics.columns = [
                "metric",
                "score"
            ]

        # -----------------------------
        # Simulation pipeline
        # -----------------------------
        else:

            metrics = None

        if job is not None:

            job["progress"] = 90
            job["status"] = "Preparing Results"

            job["progress"] = 100
            job["status"] = "Completed"

        logging.info("ML Pipeline completed successfully.")

        return {
            "run_id": result["run_id"],
            "metrics": metrics
        }