// Infrastructure Destruction Pipeline with Backup
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
        stage('Backup Data') {
            steps {
                dir('terraform') {
                    sh '''
                    mkdir -p backups/$(date +%Y%m%d_%H%M%S)
                    BACKUP_DIR=backups/$(date +%Y%m%d_%H%M%S)
                    
                    # Backup Firestore
                    gcloud firestore export gs://$(terraform output -raw swift_equivalent_bucket_name)/firestore-backup/$(date +%Y%m%d_%H%M%S)
                    
                    # Backup Storage bucket contents
                    gsutil -m cp -r gs://$(terraform output -raw swift_equivalent_bucket_name)/* $BACKUP_DIR/ || true
                    
                    # Archive local backup
                    tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR/
                    '''
                }
            }
        }
        stage('Terraform Destroy') {
            steps {
                input 'Approve infrastructure destruction? (Backup completed)'
                dir('terraform') {
                    sh 'terraform destroy -auto-approve'
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'terraform/backups/*.tar.gz, terraform/terraform.tfstate*', fingerprint: true
            cleanWs()
        }
    }
}
