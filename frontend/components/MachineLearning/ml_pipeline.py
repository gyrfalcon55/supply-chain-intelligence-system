import streamlit as st
import time
import requests
import os

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")



st.title("Machine Learning Pipeline")
st.write('The whole pipeline can be tracked on Mlflow')

# start_pipeline = st.column(1)

def start_pipeline():

    response = requests.post(
        f"{API_URL}/ml_pipeline"
    )

    return response.json()["job_id"]



if st.button(
    "Start ML Pipeline",
    icon="⚙️",
    width="stretch"
):

    job_id = start_pipeline()

    my_bar = st.progress(0)

    status = st.empty()

    while True:

        response = requests.get(
            f"{API_URL}/ml_pipeline/status/{job_id}"
        )

        data = response.json()

        my_bar.progress(
            data["progress"],
            text=f"{data['status']} ({data['progress']}%)"
        )

        status.write(data["status"])

        if data["status"] == "Completed":

            st.success("Pipeline completed successfully.")

            st.dataframe(data["metrics"])

            break

        if data["status"] == "Failed":

            st.error(data["error"])

            break

        time.sleep(1)

    my_bar.empty()