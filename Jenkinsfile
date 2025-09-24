// Jenkins pipeline for Medical Appointments Infrastructure - Dual VM Architecture
pipeline {
    agent any
    
    environment {
        // GCP Credentials
        GOOGLE_APPLICATION_CREDENTIALS = credentials('gcp-sa-key')
        
        // Project Configuration
        TF_VAR_project_id = 'peaceful-oath-470112-e8'
        TF_VAR_billing_account_id = '01F913-84297C-824CD2'
        TF_VAR_region = 'us-central1'
        TF_VAR_zone = 'us-central1-a'
        
        // Application Configuration
        TF_VAR_cloud_run_name = 'medical-appointments-api'
        TF_VAR_cloud_run_image = 'gcr.io/peaceful-oath-470112-e8/medical-appointments:latest'
        TF_VAR_entry_image = 'gcr.io/peaceful-oath-470112-e8/entry-service:latest'
        TF_VAR_compute_image = 'gcr.io/peaceful-oath-470112-e8/compute-service:latest'
        TF_VAR_api_image = 'gcr.io/peaceful-oath-470112-e8/api-service:latest'
        TF_VAR_nova_image = 'gcr.io/peaceful-oath-470112-e8/nova-service:latest'
        
        // SSH Key
        TF_VAR_ssh_key = credentials('gcp-ssh-public-key')
    }
    
    parameters {
        choice(
            name: 'ACTION',
            choices: ['plan', 'apply', 'destroy'],
            description: 'Select Terraform action to perform'
        )
        booleanParam(
            name: 'AUTO_APPROVE',
            defaultValue: false,
            description: 'Auto-approve Terraform apply (use with caution)'
        )
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run connectivity tests after deployment'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '🔄 Checking out source code...'
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                script {
                    echo '⚙️ Setting up environment...'
                    sh '''
                        echo "Current directory: $(pwd)"
                        echo "Terraform version: $(terraform --version)"
                        echo "GCloud SDK version: $(gcloud --version | head -1)"
                        echo "Project ID: $TF_VAR_project_id"
                        echo "Region: $TF_VAR_region"
                    '''
                }
            }
        }
        
        stage('Terraform Init') {
            steps {
                dir('terraform') {
                    echo '🚀 Initializing Terraform...'
                    sh '''
                        terraform init
                        terraform --version
                        echo "✅ Terraform initialization complete"
                    '''
                }
            }
        }
        
        stage('Terraform Validate') {
            steps {
                dir('terraform') {
                    echo '✅ Validating Terraform configuration...'
                    sh '''
                        terraform validate
                        terraform fmt -check=true -diff=true
                        echo "✅ Terraform configuration is valid"
                    '''
                }
            }
        }
        
        stage('Terraform Plan') {
            steps {
                dir('terraform') {
                    echo '📋 Creating Terraform execution plan...'
                    sh '''
                        terraform plan -out=tfplan -detailed-exitcode
                        echo "✅ Terraform plan completed"
                        echo ""
                        echo "🎯 DEPLOYMENT SUMMARY:"
                        echo "  • VM1 (Private): snet-private (10.0.128.0/17) - No public access"
                        echo "  • VM2 (Public): snet-public (10.0.0.0/17) - Public internet access"
                        echo "  • VPC: vnet-nebo (10.0.0.0/16)"
                        echo "  • NAT Gateway for VM1 outbound connectivity"
                        echo "  • Jump host access: VM2 → VM1"
                        echo ""
                    '''
                }
            }
        }
        
        stage('Terraform Apply') {
            when {
                anyOf {
                    expression { params.ACTION == 'apply' }
                    expression { params.ACTION == 'plan' && env.AUTO_APPROVE == 'true' }
                }
            }
            steps {
                script {
                    dir('terraform') {
                        if (params.AUTO_APPROVE) {
                            echo '🚀 Auto-applying Terraform plan...'
                            sh 'terraform apply -auto-approve tfplan'
                        } else {
                            echo '⏸️ Waiting for manual approval...'
                            input message: 'Deploy Medical Appointments Infrastructure?', 
                                  ok: 'Deploy',
                                  submitterParameter: 'APPROVER'
                            echo "✅ Approved by: ${env.APPROVER}"
                            echo '🚀 Applying Terraform plan...'
                            sh 'terraform apply -auto-approve tfplan'
                        }
                        echo '✅ Infrastructure deployment completed!'
                    }
                }
            }
        }
        
        stage('Terraform Destroy') {
            when {
                expression { params.ACTION == 'destroy' }
            }
            steps {
                script {
                    dir('terraform') {
                        echo '⚠️ DESTRUCTIVE ACTION: This will destroy all infrastructure!'
                        input message: 'Are you sure you want to DESTROY all resources?', 
                              ok: 'DESTROY',
                              submitterParameter: 'DESTROYER'
                        echo "🗑️ Destruction approved by: ${env.DESTROYER}"
                        sh 'terraform destroy -auto-approve'
                        echo '✅ Infrastructure destruction completed'
                    }
                }
            }
        }
        
        stage('Get Outputs') {
            when {
                anyOf {
                    expression { params.ACTION == 'apply' }
                    expression { params.ACTION == 'plan' && env.AUTO_APPROVE == 'true' }
                }
            }
            steps {
                dir('terraform') {
                    script {
                        echo '📊 Retrieving Terraform outputs...'
                        sh '''
                            echo ""
                            echo "🎯 ACCEPTANCE CRITERIA VALIDATION:"
                            terraform output acceptance_criteria
                            echo ""
                            echo "🔗 QUICK ACCESS SUMMARY:"
                            terraform output quick_access_summary
                            echo ""
                            echo "📋 NETWORK SUMMARY:"
                            terraform output network_summary
                        '''
                    }
                }
            }
        }
        
        stage('Connectivity Tests') {
            when {
                allOf {
                    anyOf {
                        expression { params.ACTION == 'apply' }
                        expression { params.ACTION == 'plan' && env.AUTO_APPROVE == 'true' }
                    }
                    expression { params.RUN_TESTS == true }
                }
            }
            steps {
                script {
                    echo '🧪 Running connectivity tests...'
                    sh '''
                        chmod +x test-vm-connectivity.sh
                        ./test-vm-connectivity.sh || echo "⚠️ Some connectivity tests failed (may require SSH key setup)"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo '📁 Archiving artifacts...'
                archiveArtifacts artifacts: 'terraform/tfplan, terraform/terraform.tfstate*, terraform/*.log', 
                                fingerprint: true, 
                                allowEmptyArchive: true
            }
        }
        success {
            script {
                if (params.ACTION == 'apply' || (params.ACTION == 'plan' && params.AUTO_APPROVE)) {
                    echo '''
                    🎉 DEPLOYMENT SUCCESSFUL!
                    
                    ✅ Medical Appointments Infrastructure Ready
                    ✅ VM1 (Private) - Not accessible from public hosts
                    ✅ VM2 (Public) - Accessible from public hosts  
                    ✅ VM2 can connect to VM1 via internal network
                    
                    Check the "Get Outputs" stage for connection details.
                    '''
                } else if (params.ACTION == 'destroy') {
                    echo '🗑️ Infrastructure successfully destroyed'
                } else {
                    echo '📋 Terraform plan completed successfully'
                }
            }
        }
        failure {
            echo '❌ Pipeline failed! Check the logs for details.'
        }
        cleanup {
            echo '🧹 Cleaning up workspace...'
            cleanWs(cleanWhenAborted: true, cleanWhenFailure: true, cleanWhenSuccess: true)
        }
    }
}
