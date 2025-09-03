// Linting Pipeline - validates code quality
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Terraform Format Check') {
            steps {
                dir('terraform') {
                    sh 'terraform fmt -check=true -diff=true'
                }
            }
        }
        stage('Terraform Validate') {
            steps {
                dir('terraform') {
                    sh 'terraform init -backend=false'
                    sh 'terraform validate'
                }
            }
        }
        stage('TFLint') {
            steps {
                dir('terraform') {
                    sh '''
                    if ! command -v tflint &> /dev/null; then
                        curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
                    fi
                    tflint --init
                    tflint --format=compact
                    '''
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
