pipeline {
    agent any
    
    environment {
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        AWS_DEFAULT_REGION    = 'us-east-1'  // Add this line
    }
    
    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t lambda-image docker/'
            }
        }
        
        stage('Push to ECR') {
            steps {
                script {
                    ecr_repo = "145023133800.dkr.ecr.us-east-1.amazonaws.com/lambda-ecr-repo"
                    sh "aws ecr get-login-password | docker login --username AWS --password-stdin ${ecr_repo}"
                    sh "docker tag lambda-image ${ecr_repo}:latest"
                    sh "docker push ${ecr_repo}:latest"
                }
            }
        }
        
        stage('Terraform Apply') {
            steps {
                sh 'terraform -chdir=terraform init'
                sh 'terraform -chdir=terraform apply -auto-approve'
            }
        }
    }
}
