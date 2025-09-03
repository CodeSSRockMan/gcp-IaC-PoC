// Infrastructure Creation Pipeline
pipeline {
    agent any
    environment {
        GOOGLE_APPLICATION_CREDENTIALS = credentials('gcp-sa-key')
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
                input 'Approve infrastructure creation?'
                dir('terraform') {
                    sh 'terraform apply -auto-approve tfplan'
                }
            }
        }
        stage('Run Ansible Setup') {
            steps {
                sh 'ansible-playbook ansible/setup.yml -i ansible/inventory'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'terraform/tfplan, terraform/terraform.tfstate*', fingerprint: true
            cleanWs()
        }
    }
}
