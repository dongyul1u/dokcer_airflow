# Filename: download_pdf.py (to be placed in the Airflow plugins folder)
import boto3
from dotenv import load_dotenv
import os
from io import BytesIO
from PyPDF2 import PdfReader


def download_pdf(bucket_name, file_keys):
    download_path = '/opt/airflow/dags/plugins/files'
    ak = os.getenv("AWS_SK")
    aki = os.getenv("AWS_AK")
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    s3_client = boto3.client('s3',aws_access_key_id = aki, aws_secret_access_key =ak)
    
    for file_key in file_keys:
        # os.path.basename to get the last part of the path or url
        local_filename = os.path.join(download_path, os.path.basename(file_key))
        print('local_filename:', local_filename)
        s3_client.download_file(bucket_name, file_key, local_filename)

