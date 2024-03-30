import os
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

from plugins.process_pdf import process_pdf

dag = DAG(
    dag_id="handle_pdf_dag",
    schedule_interval="0 0 * * *",  # Daily at midnight
    start_date=days_ago(1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["pdf_processing", "s3", "PyPDF2"],
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

    process_pdf_task = PythonOperator(
        task_id='process_pdf',
        python_callable=process_pdf,
        op_kwargs={'bucket_name': 'your-bucket-name', 'file_key': 'path/to/your/pdf_file.pdf'},
    )

    end_task = PythonOperator(
        task_id='end_message',
        python_callable=end_message,
    )

    start_task >> process_pdf_task >> end_task
