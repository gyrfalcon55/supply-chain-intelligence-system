import numpy as np
import pandas as pd
import pytest


# ============================================================
# Feature Engineering
# ============================================================

from ml_pipeline.feature_engineering import (
    FeatureEngineeringPipeline
)


def test_daily_to_weekly_aggregation(monkeypatch):

    monkeypatch.setattr(
        "ml_pipeline.feature_engineering.load_config",
        lambda: {
            "raw_schema": {
                "schema_name": "raw_data",
                "table_name": "sales_orders"
            },
            "processed_schema": {
                "schema_name": "processed_data",
                "table_name": "processed_sales_orders"
            }
        }
    )

    pipeline = FeatureEngineeringPipeline()

    df = pd.DataFrame({
        "Product_ID": ["P1", "P1", "P1"],
        "Order_Date": [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03"
        ],
        "Order_Quantity": [
            10,
            20,
            5
        ]
    })

    result = pipeline.convert_daily_to_weekly(
        df
    )

    assert not result.empty

    assert list(result.columns) == [
        "Product_ID",
        "Order_Date",
        "Order_Quantity"
    ]

    assert result["Order_Quantity"].sum() == 35


def test_change_column_names(monkeypatch):

    monkeypatch.setattr(
        "ml_pipeline.feature_engineering.load_config",
        lambda: {
            "raw_schema": {
                "schema_name": "raw_data",
                "table_name": "sales_orders"
            },
            "processed_schema": {
                "schema_name": "processed_data",
                "table_name": "processed_sales_orders"
            }
        }
    )

    pipeline = FeatureEngineeringPipeline()

    df = pd.DataFrame({
        "Product_ID": ["P1", "P2"],
        "Order_Date": pd.to_datetime([
            "2024-01-07",
            "2024-01-14"
        ]),
        "Order_Quantity": [10, 20]
    })

    result = pipeline.change_column_names(
        df
    )

    assert list(result.columns) == [
        "unique_id",
        "ds",
        "y"
    ]

    assert result["unique_id"].tolist() == [
        "P1",
        "P2"
    ]

    assert result["y"].tolist() == [
        10,
        20
    ]


# ============================================================
# Preprocessing
# ============================================================

from ml_pipeline.preprocessing import (
    PreprocessingPipeline
)


def test_fill_missing_dates(monkeypatch):

    monkeypatch.setattr(
        "ml_pipeline.preprocessing.load_config",
        lambda: {
            "processed_schema": {
                "schema_name": "processed_data",
                "table_name": "processed_sales_orders"
            }
        }
    )

    pipeline = PreprocessingPipeline()

    df = pd.DataFrame({
        "unique_id": [
            "P1",
            "P1",
            "P2",
            "P2"
        ],
        "ds": pd.to_datetime([
            "2024-01-07",
            "2024-01-21",
            "2024-01-07",
            "2024-01-21"
        ]),
        "y": [
            10,
            20,
            5,
            15
        ]
    })

    result = pipeline.fill_missing_dates(
        df
    )

    assert not result.empty

    # Missing 2024-01-14 should have been created
    p1 = result[
        result["unique_id"] == "P1"
    ]

    assert len(p1) == 3

    missing_week = p1[
        p1["ds"] == pd.Timestamp("2024-01-14")
    ]

    assert len(missing_week) == 1
    assert missing_week.iloc[0]["y"] == 0


# ============================================================
# Training Pipeline
# ============================================================

from ml_pipeline.training_pipeline import (
    TrainingPipeline
)


def test_split_data(monkeypatch):

    monkeypatch.setattr(
        "ml_pipeline.training_pipeline.load_config",
        lambda: {
            "processed_schema": {
                "schema_name": "processed_data",
                "table_name": "processed_sales_orders"
            },
            "evaluation_schema": {
                "schema_name": "evaluation_data",
                "test_data": "evaluation_test",
                "train_data": "evaluation_train"
            },
            "forecasting": {
                "schema_name": "forecast_data",
                "table_name": "forecast_sales_orders",
                "frequency": "W",
                "horizon": 2
            },
            "artifacts": {
                "model_dir": "artifacts/models"
            }
        }
    )

    pipeline = TrainingPipeline()

    dates = pd.date_range(
        "2024-01-07",
        periods=12,
        freq="W"
    )

    df = pd.DataFrame({
        "unique_id": ["P1"] * 12,
        "ds": dates,
        "y": range(1, 13)
    })

    train, test = pipeline.split_data(
        df,
        horizon=2
    )

    assert len(train) == 10
    assert len(test) == 2

    assert (
        train["ds"].max()
        < test["ds"].min()
    )


def test_predict_output():

    class FakeModel:

        def predict(self, h):

            return pd.DataFrame({
                "unique_id": ["P1"] * h,
                "ds": pd.date_range(
                    "2024-04-01",
                    periods=h,
                    freq="W"
                ),
                "CrostonClassic": [10] * h
            })

    model = FakeModel()

    pipeline = object.__new__(
        TrainingPipeline
    )

    result = pipeline.predict_output(
        model,
        horizon=2
    )

    assert len(result) == 2

    assert "CrostonClassic" in result.columns

    assert result[
        "CrostonClassic"
    ].notna().all()


# ============================================================
# Model Evaluation
# ============================================================

from ml_pipeline.evaluation import (
    ModelEvaluation
)


def test_create_eval_df(monkeypatch):

    monkeypatch.setattr(
        "ml_pipeline.evaluation.load_config",
        lambda: {
            "evaluation_schema": {
                "schema_name": "evaluation_data",
                "test_data": "evaluation_test",
                "train_data": "evaluation_train"
            },
            "forecasting": {
                "schema_name": "forecast_data",
                "table_name": "forecast_sales_orders"
            }
        }
    )

    evaluator = ModelEvaluation()

    test_df = pd.DataFrame({
        "unique_id": ["P1", "P2"],
        "ds": pd.to_datetime([
            "2024-01-07",
            "2024-01-07"
        ]),
        "y": [10, 20]
    })

    forecast_df = pd.DataFrame({
        "unique_id": ["P1", "P2"],
        "ds": pd.to_datetime([
            "2024-01-07",
            "2024-01-07"
        ]),
        "CrostonClassic": [8, 18]
    })

    result = evaluator.create_eval_df(
        test_df,
        forecast_df
    )

    assert not result.empty

    assert len(result) == 2

    assert "y" in result.columns
    assert "CrostonClassic" in result.columns

    assert result.isnull().sum().sum() == 0


# ============================================================
# Procurement Logic
# ============================================================

from backend.pipelines.procurements_pipeline import (
    return_existing_orders,
    return_new_orders
)


def test_return_new_orders():

    new_proc = pd.DataFrame({
        "Product_ID": [
            "P1",
            "P2",
            "P3"
        ],
        "Supplier_ID": [
            "S1",
            "S2",
            "S3"
        ]
    })

    result = return_new_orders(
        new_proc
    )

    assert isinstance(
        result,
        pd.DataFrame
    )


# ============================================================
# Basic Forecast Output Contract
# ============================================================

def test_forecast_output_contract():

    forecast = pd.DataFrame({
        "unique_id": [
            "P1",
            "P2"
        ],
        "ds": pd.to_datetime([
            "2024-10-06",
            "2024-10-06"
        ]),
        "CrostonClassic": [
            10.0,
            20.0
        ]
    })

    required_columns = {
        "unique_id",
        "ds",
        "CrostonClassic"
    }

    assert required_columns.issubset(
        forecast.columns
    )

    assert forecast[
        "unique_id"
    ].notna().all()

    assert forecast[
        "ds"
    ].notna().all()

    assert forecast[
        "CrostonClassic"
    ].notna().all()

    assert (
        forecast["CrostonClassic"] >= 0
    ).all()