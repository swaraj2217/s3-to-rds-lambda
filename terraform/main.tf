provider "aws" {
  region = "us-east-1"
}

# S3 Bucket
resource "aws_s3_bucket" "data_bucket" {
  bucket = "mys3buck22"
  force_destroy = true  # Allow Terraform to delete the bucket if needed
}

# ECR Repository
resource "aws_ecr_repository" "lambda_repo" {
  name = "lambda-ecr-repo"
  force_delete = true  # Allow Terraform to delete the repository if needed
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda-exec-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Attach IAM Policies to the Role
resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "rds_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSDataFullAccess"
}

resource "aws_iam_role_policy_attachment" "glue_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
}

# Lambda Function
resource "aws_lambda_function" "data_processor" {
  function_name = "data-processor"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "145023133800.dkr.ecr.us-east-1.amazonaws.com/lambda-ecr-repo:latest"
  
  environment {
    variables = {
      RDS_HOST     = "database-1.c3oc4ci4s9s0.us-east-1.rds.amazonaws.com"
      RDS_DB       = "database-1"
      RDS_USER     = "admin"
      RDS_PASSWORD = "swarajdb"
    }
  }
}

# S3 Event Trigger for Lambda
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.data_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.data_processor.arn
    events              = ["s3:ObjectCreated:*"]
  }
}

# Lambda Permission for S3
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.data_bucket.arn
}
