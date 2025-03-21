# scripts/update_employee_data.py - Script to upload sample employee data to S3
import boto3
import csv
import datetime
import os
import boto3

# Initialize S3 client
s3 = boto3.client('s3')

BUCKET_NAME = 'sfbucket2025'  # Target S3 bucket for 2025 ETL pipeline
PREFIX = 'employee_'           # Prefix for timestamped CSV files

def generate_sample_data():
    """Generate sample employee data for testing."""
    return [
        {'first': 'Alice', 'last': 'Brown', 'age': 30, 'sex': 'F'},
        {'first': 'Charlie', 'last': 'Davis', 'age': 40, 'sex': 'M'}
    ]

def upload_to_s3(data):
    """Upload sample data to S3 with a timestamped filename for optimization."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{PREFIX}{timestamp}.csv"
    local_path = f"/tmp/{filename}"
    
    # Write sample data to a local CSV file
    with open(local_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['first', 'last', 'age', 'sex'])
        writer.writeheader()
        writer.writerows(data)
    
    # Upload to S3
    s3.upload_file(local_path, BUCKET_NAME, filename)
    os.remove(local_path)  # Clean up local file
    print(f"Uploaded {filename} to s3://{BUCKET_NAME}/{filename}")
    return filename

if __name__ == "__main__":
    """Main script entrypoint."""
    data = generate_sample_data()
    uploaded_file = upload_to_s3(data)
    print(f"New file {uploaded_file} uploaded. Pipeline will auto-trigger via S3 event.")