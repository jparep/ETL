# lambda/lambda_function.py - AWS Lambda function for ETL: Extract from S3, Transform with pandas, Load into Snowflake
import json
import boto3
import csv
import pandas as pd
import snowflake.connector
import logging
import os
from datetime import datetime

# Configure logging for detailed tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize S3 client for data extraction
s3 = boto3.client('s3')

def get_snowflake_credentials():
    """Fetch Snowflake credentials from AWS Secrets Manager or use mock for local testing."""
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):  # Running in AWS Lambda
        secrets_client = boto3.client("secretsmanager")
        secret_name = os.getenv("SNOWFLAKE_SECRET_NAME", "snowflake_credentials")
        try:
            response = secrets_client.get_secret_value(SecretId=secret_name)
            secret_dict = json.loads(response["SecretString"])
            return {
                "user": secret_dict["SNOWFLAKE_USER"],
                "password": secret_dict["SNOWFLAKE_PASSWORD"],
                "account": secret_dict["SNOWFLAKE_ACCOUNT"],
                "warehouse": secret_dict["SNOWFLAKE_WAREHOUSE"],
                "database": secret_dict["SNOWFLAKE_DATABASE"],
                "schema": secret_dict["SNOWFLAKE_SCHEMA"],
            }
        except Exception as e:
            logging.error(f"Failed to fetch Snowflake credentials: {e}")
            raise
    else:  # Local testing
        logging.info("Running locally; using mock Snowflake credentials.")
        return {
            "user": "jparep",  # Replace with your local Snowflake username
            "password": "your-password",  # Replace with your local Snowflake password
            "account": "kjdoqdf-xu95576",  # Replace with your Snowflake account
            "warehouse": "compute_wh",
            "database": "employee_db",
            "schema": "employee",
        }

def transform_data(df):
    """Transform the DataFrame: clean data, categorize ages, and standardize sex."""
    logger.info("Transforming data...")
    # Clean and standardize data
    df['first'] = df['first'].str.strip().str.title()
    df['last'] = df['last'].str.strip().str.title()
    df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0).astype(int)
    df['sex'] = df['sex'].str.upper().replace({'MALE': 'M', 'FEMALE': 'F'}).fillna('Unknown')

    # Categorize ages into groups
    df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 45, float('inf')], 
                            labels=['Under 25', '25-35', '36-45', 'Over 45'], 
                            include_lowest=True)

    # Add load timestamp
    df['load_time'] = datetime.now()

    logger.info(f"Transformed data shape: {df.shape}")
    return df

def load_to_snowflake(df):
    """Load transformed data into Snowflake."""
    try:
        logger.info("Loading data into Snowflake...")
        SNOWFLAKE_CONFIG = get_snowflake_credentials()
        if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):  # Local testing
            logging.info("Skipping actual Snowflake load in local testing; mocking success.")
            return  # Mock the load for local testing
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()

        # Ensure table exists with correct schema
        create_table_sql = """
        CREATE OR REPLACE TABLE employee_db.employee.employees (
            first STRING,
            last STRING,
            age INT,
            sex STRING,
            age_group STRING,
            load_time TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)

        # Insert transformed data
        insert_sql = """
        INSERT INTO employee_db.employee.employees (first, last, age, sex, age_group, load_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = [tuple(row) for row in df[['first', 'last', 'age', 'sex', 'age_group', 'load_time']].values]
        cursor.executemany(insert_sql, data)

        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Data loaded into Snowflake successfully.")
    except Exception as e:
        logging.error(f"Error loading to Snowflake: {e}")
        raise

def lambda_handler(event, context):
    """
    AWS Lambda function triggered by S3 upload, performing ETL: Extract, Transform, Load.
    Args:
        event: S3 event data from Lambda trigger
        context: Lambda context object
    Returns:
        dict: HTTP response with status code and message
    """
    try:
        for record in event["Records"]:
            bucket_name = record["s3"]["bucket"]["name"]
            object_key = record["s3"]["object"]["key"]

            logger.info(f"Processing file: {object_key} from bucket: {bucket_name}")

            # Extract: Read CSV from S3 (or simulate for local testing)
            if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                response = s3.get_object(Bucket=bucket_name, Key=object_key)
                df = pd.read_csv(response['Body'])
            else:  # Local testing
                logger.info("Simulating S3 data for local testing...")
                sample_data = [
                    {'first': 'Alice', 'last': 'Brown', 'age': 30, 'sex': 'F'},
                    {'first': 'Charlie', 'last': 'Davis', 'age': 40, 'sex': 'M'}
                ]
                df = pd.DataFrame(sample_data)

            # Transform: Clean and enrich data
            transformed_df = transform_data(df)

            # Load: Insert into Snowflake
            load_to_snowflake(transformed_df)

            logger.info(f"✅ Completed ETL for {object_key}.")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Processed and loaded {object_key} into Snowflake"})
        }

    except Exception as e:
        logger.error(f"Error in ETL process: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

if __name__ == "__main__":
    # Simulate Lambda invocation for local testing
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "sfbucket2025"},
                    "object": {"key": "employee_20250223_120000.csv"}
                }
            }
        ]
    }
    lambda_handler(event, None)