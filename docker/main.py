import boto3
import psycopg2
import os

def handler(event, context):
    # Get S3 bucket and file details
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Read file from S3
    s3 = boto3.client('s3')
    file_content = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
    
    # Try writing to RDS
    try:
        conn = psycopg2.connect(
            host="database-1.c3oc4ci4s9s0.us-east-1.rds.amazonaws.com",
            dbname="database-1",
            user="admin",
            password="swarajdb"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO data_table (content) VALUES (%s)", (file_content,))
        conn.commit()
        print("Data written to RDS")
        
    except Exception as e:
        print(f"RDS Error: {e}")
        # Fallback to Glue
        glue = boto3.client('glue')
        try:
            glue.put_record(
                DatabaseName='my_glue_database',
                TableName='my_glue_table',
                Record={'content': file_content}
            )
            print("Data written to Glue")
        except Exception as glue_error:
            print(f"Glue Error: {glue_error}")
            return {"status": 500, "message": "Failed to write to RDS and Glue"}
    
    return {"status": 200, "message": "Data processed successfully"}
