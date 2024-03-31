# Filename: process_pdf.py (to be placed in the Airflow plugins folder)

import boto3
from dotenv import load_dotenv
import os
from io import BytesIO
from PyPDF2 import PdfReader


load_dotenv(override=True)

ak = os.getenv("AWS_SK")
aki = os.getenv("AWS_AK")
print(ak,aki)

def process_pdf(bucket_name, file_key):
    """
    Download a PDF from S3, read its content using PyPDF2, and print the text of each page.

    :param bucket_name: Name of the S3 bucket
    :param file_key: Key of the file in the S3 bucket
    """
    # Create an S3 resource
    s3 = boto3.client('s3',aws_access_key_id = aki, aws_secret_access_key =ak)
    s3_response_object = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = s3_response_object['Body'].read()
    print(type(file_content))

    # transfer to IO
    pdf_io = BytesIO(file_content)

    # use BytesIO object to PdfReader
    pdf_reader = PdfReader(pdf_io)
    
    for page in pdf_reader.pages:
        print(page.extract_text())
