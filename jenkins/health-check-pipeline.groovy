// Health Check Pipeline
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
        stage('Infrastructure Health Check') {
            steps {
                dir('terraform') {
                    sh '''
                    # Check Cloud Run services
                    curl -f $(terraform output -raw cloud_run_entry_url) || exit 1
                    curl -f $(terraform output -raw cloud_run_api_url) || exit 1
                    curl -f $(terraform output -raw cloud_run_compute_url) || exit 1
                    
                    # Check Firestore connectivity
                    gcloud firestore databases list --project=$(terraform output -raw project_id)
                    
                    # Check storage bucket
                    gsutil ls gs://$(terraform output -raw swift_equivalent_bucket_name)
                    '''
                }
            }
        }
        stage('Run Ansible Health Checks') {
            steps {
                sh 'ansible-playbook ansible/health-check.yml -i ansible/inventory'
            }
        }
    }
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'health-check.html',
                reportName: 'Health Check Report'
            ])
            cleanWs()
        }
    }
}
