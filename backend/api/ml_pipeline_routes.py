from fastapi import APIRouter
from ml_pipeline.ML_Orchestration import Ml_Pipeline
from threading import Thread
from backend.services.job_store import jobs
import uuid
import mlflow
router = APIRouter()


def run_job(job_id):

    job = jobs[job_id]

    try:

        pipeline = Ml_Pipeline()

        metrics = pipeline.run_initial_pipeline(job)

        job["metrics"] = metrics.to_dict(
            orient="records"
        )

        job["status"] = "Completed"

        job["progress"] = 100

    except Exception as e:

        job["status"] = "Failed"

        job["error"] = str(e)

@router.post("/ml_pipeline")
def start_pipeline():

    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "Running",
        "progress": 0,
        "metrics": None,
        "error": None
    }

    Thread(
        target=run_job,
        args=(job_id,),
        daemon=True
    ).start()

    return {
        "job_id": job_id
    }

@router.get("/ml_pipeline/status/{job_id}")
def pipeline_status(job_id: str):
    return jobs[job_id]