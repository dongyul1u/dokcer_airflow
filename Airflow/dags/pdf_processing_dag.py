import os
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

from plugins.process_pdf import process_pdf
from plugins.download_pdf import download_pdf
from plugins.grobid_parsing import PDF_XML_function


dag = DAG(
    dag_id="handle_pdf_dag",
    schedule_interval="0 0 * * *",  # Daily at midnight
    start_date=days_ago(1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["pdf_processing", "s3", "snowflake"],
)

def start_message():
    print("Starting PDF processing task")

def end_message():
    print("PDF processing task completed")


with dag:
    start_task = PythonOperator(
        task_id='start_message',
        python_callable=start_message,
    )

    download_pdf_task = PythonOperator(
        task_id='download_pdf',
        python_callable=download_pdf,
        op_kwargs={
            'bucket_name': "{{ dag_run.conf['bucket_name'] }}",
            'file_keys': "{{ dag_run.conf['file_keys'] }}"
        },
    )


    grobid_parsing_task = PythonOperator(
        task_id='grobid_pdf_to_xml',
        python_callable=PDF_XML_function,
        op_kwargs={
            'pdf_files': "{{ dag_run.conf['file_keys'] }}"
        },
    )

    end_task = PythonOperator(
        task_id='end_message',
        python_callable=end_message,
    )

    start_task >> download_pdf_task >> grobid_parsing_task >> end_task
