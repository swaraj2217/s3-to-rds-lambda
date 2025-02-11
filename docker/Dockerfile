FROM public.ecr.aws/lambda/python:3.8

# Copy Python script
COPY main.py .

# Install dependencies
RUN pip install boto3 psycopg2-binary

# Set Lambda handler
CMD ["main.handler"]
