import streamlit as st
import requests
import boto3
from dotenv import load_dotenv
import os

load_dotenv(override=True)

ak = os.getenv("AWS_SK")
aki = os.getenv("AWS_AK")


# Streamlit UI
st.title("Welcome to our application")
st.header("Big Data Project - Team03")
st.subheader("Airflow work flow")
# Number of PDF files input
number_of_files = st.number_input("Please enter the number of PDF files", min_value=1, max_value=10, step=1)

uploaded_files = None

if number_of_files > 0:
        uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if st.button("Triger"):
    if uploaded_files is not None and len(uploaded_files) == number_of_files:
        st.success("Uploading files...")
        
        # Hardcoded S3 bucket name
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        
        # Create an S3 resource
        s3_resource = boto3.resource('s3',aws_access_key_id = aki, aws_secret_access_key =ak)

        # Iterate through the uploaded files and upload to S3
        s3_keys = []  # Store S3 URLs
        for file in uploaded_files:
            file_bytes = file.read()
            file_name = file.name  # Get the original file name

            # Upload the file to S3
            s3_resource.Bucket(BUCKET_NAME).put_object(
                Key=file_name,
                Body=file_bytes
            )
            
            # Construct S3 URL
            s3_key = f"{file_name}"
            s3_keys.append(s3_key)

        s3_urls = {
            'file_keys':s3_keys
        }

        st.write(s3_urls)
        st.success("All files uploaded!")



        # Trigger FastAPI service and provide S3 locations
        try:
            response = requests.post("http://fastapi:8000/trigger-airflow/", json=s3_urls)
            response.raise_for_status()  # Raise exception for non-200 status codes
            st.success(response.json().get('message'))
        except requests.exceptions.HTTPError as err:
            error_detail = err.response.json().get('detail', 'Unknown error')  # get the detail of error, if not print "Unknow error"
            st.error(f"Error: {error_detail}")  # show streamlit
        except Exception as e:
            st.error(f"An error occurred: {e}")
    elif uploaded_files is not None:
        st.warning(f"Please upload exactly {number_of_files} files.")