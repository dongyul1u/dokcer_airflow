# from fastapi import FastAPI, HTTPException
# import requests
# from requests.auth import HTTPBasicAuth

# app = FastAPI()

# @app.post("/trigger-airflow/")
# async def trigger_airflow(s3_locations: list[str]):
#     print("Received S3 locations:", s3_locations)
#     airflow_api_url = "http://damg-assignment04-airflow-webserver-1:8080/api/v1/dags/pdf_processing_dag/dagRuns"

#     for s3_location in s3_locations:
#         payload = {
#             "conf": {"s3_location": s3_location}
#         }

#         try:
#             response = requests.post(airflow_api_url, json=payload,auth=HTTPBasicAuth('airflow','airflow'))

#             if response.status_code == 200:
#                 return {"message": "DAG run triggered successfully"}
#             else:
#                 raise HTTPException(status_code=response.status_code, detail=response.text)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


from fastapi import FastAPI, HTTPException
import requests  # To make HTTP requests to Airflow's REST API
import os
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv(override=True)

class Files(BaseModel):
    file_keys:list[str]

app = FastAPI()


@app.post("/trigger-airflow/")
async def trigger_pdf_processing(files: Files):
    bucket_name = os.getenv("BUCKET_NAME")
    file_keys = files.file_keys
    # Construct the payload for the Airflow DAG trigger
    for file_key in file_keys:
        dag_trigger_payload = {
            "conf": {
                "bucket_name": bucket_name,
                "file_key": file_key
            }
        }

        # URL for the Airflow REST API endpoint to trigger a DAG
        airflow_dag_trigger_url = "http://dokcer_airflow-airflow-webserver-1:8080/api/v1/dags/handle_pdf_dag/dagRuns"
        
        # Authentication for Airflow (adjust as needed)
        airflow_auth = ("airflow", "airflow")
        try:
            # Make the request to Airflow to trigger the DAG
            response = requests.post(
                airflow_dag_trigger_url,
                json=dag_trigger_payload,
                auth=airflow_auth
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to trigger Airflow for s3_url {file_key}: {err}")

    return {
        "message": f"DAG triggered successfully, upload {file_keys}",
        }


