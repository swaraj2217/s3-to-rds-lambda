import boto3
import psycopg2
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def handler(event, context):
    try:
        # Get S3 bucket and file details
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Reading file from S3: Bucket={bucket}, Key={key}")

        # Read file from S3
        s3 = boto3.client('s3')
        file_content = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
        logger.info("File content read successfully from S3")

        # Try writing to RDS
        try:
            conn = psycopg2.connect(
                host="database-1.c3oc4ci4s9s0.us-east-1.rds.amazonaws.com",
                dbname="database-1",
                user="admin",
                password="swarajdb"
            )
            cursor = conn.cursor()
            logger.info("Connected to RDS successfully")

            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_table (
                    id SERIAL PRIMARY KEY,
                    content TEXT
                )
            """)
            conn.commit()
            logger.info("Created table 'data_table' (if it didn't exist)")

            # Insert data into RDS
            cursor.execute("INSERT INTO data_table (content) VALUES (%s)", (file_content,))
            conn.commit()
            logger.info("Data written to RDS successfully")

        except Exception as e:
            logger.error(f"RDS Error: {e}")
            # Fallback to Glue
            glue = boto3.client('glue')
            try:
                glue.put_record(
                    DatabaseName='my_glue_database',
                    TableName='my_glue_table',
                    Record={'content': file_content}
                )
                logger.info("Data written to Glue successfully")
            except Exception as glue_error:
                logger.error(f"Glue Error: {glue_error}")
                return {"status": 500, "message": "Failed to write to RDS and Glue"}

    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        return {"status": 500, "message": "An unexpected error occurred"}

    return {"status": 200, "message": "Data processed successfully"}
