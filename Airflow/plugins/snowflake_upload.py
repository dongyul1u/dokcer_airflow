import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from sqlalchemy import create_engine
import bcrypt
import os
import csv
load_dotenv()

def convert_to_url(column_data, bucket_name):
    # Constructing the URL based on the first column data
    trimmed_data = column_data[5:7]
    url = f"https://s3.console.aws.amazon.com/s3/object/{bucket_name}?region=us-east-1&bucketType=general&prefix=Grobid_RR_2024_{trimmed_data}_combined.txt"
    return url

u: str | None=os.getenv("BUCKET_NAME")
files_path = os.getenv('AIRFLOW_FILES_PATH')


if files_path is not None:
  file_path = files_path + '/metadata.csv'
  # Open the CSV file for reading and writing
  with open(file_path, mode='r') as file:
      reader = csv.DictReader(file)
      # make sequence to list
      original_fieldnames = list(reader.fieldnames) if reader.fieldnames else []
      fieldnames = original_fieldnames + ['URL']
      
      # Create a new CSV file with an additional column for the URLs
      with open(f'{files_path}/metadata_new.csv', mode='w', newline='') as output_file:
          writer = csv.DictWriter(output_file, fieldnames=fieldnames)
          writer.writeheader()
          
          # Iterate over each row in the CSV file
          for row in reader:
              column_data = row['filename']  # Assuming the first column contains the data for conversion
              url = convert_to_url(column_data, u)
              row['URL'] = url
              
              # Write the modified row to the new CSV file
              writer.writerow(row)

