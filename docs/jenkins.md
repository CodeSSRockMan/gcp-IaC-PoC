# Jenkins Pipelines

## Available Pipelines

### 1. Linting Pipeline (`lint-pipeline.groovy`)
- Validates Terraform code formatting
- Runs terraform validate
- TFLint security/best practice checks

### 2. Create Infrastructure (`create-pipeline.groovy`)
- Initializes Terraform
- Plans and applies infrastructure  
- Runs Ansible setup playbooks
- Archives state files

### 3. Destroy Infrastructure (`destroy-pipeline.groovy`)
- Backs up Firestore and Storage data
- Destroys all infrastructure
- Archives backups locally

### 4. Health Check (`health-check-pipeline.groovy`)
- Tests all service endpoints
- Runs Ansible health checks
- Generates HTML report

## Setup
1. Create Jenkins credential `gcp-sa-key` (GCP service account JSON)
2. Install required tools: terraform, ansible, gcloud SDK
3. Create pipeline jobs pointing to respective .groovy files

## Local Storage
- State files: Jenkins archives terraform.tfstate*
- Backups: Stored in Jenkins workspace under backups/
- Health reports: Published as HTML artifacts
