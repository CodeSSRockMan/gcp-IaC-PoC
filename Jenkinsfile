// Jenkins pipeline definition
pipeline {
    agent any
    environment {
        GOOGLE_APPLICATION_CREDENTIALS = credentials('gcp-sa-key') // Jenkins secret with GCP service account JSON
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Terraform Init') {
            steps {
                dir('terraform') {
                    sh 'terraform init'
                }
            }
        }
        stage('Terraform Plan') {
            steps {
                dir('terraform') {
                    sh 'terraform plan -out=tfplan'
                }
            }
        }
        stage('Terraform Apply') {
            steps {
                input 'Approve apply?'
                dir('terraform') {
                    sh 'terraform apply -auto-approve tfplan'
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
