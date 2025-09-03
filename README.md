# GCP Infrastructure as Code (IaC) PoC

## Overview
This project creates an OpenStack-equivalent infrastructure on Google Cloud Platform using Terraform, automated with Jenkins pipelines and configured with Ansible.

## Architecture
- **Entry Service**: Load balancer/gateway (python jumphost + web interface)
- **API Service**: Controller that manages resources and validates requests
- **Compute Service**: Performs actual workload operations
- **Storage**: Swift-equivalent (Cloud Storage) + Firestore database

## Quick Start
1. Copy `terraform/terraform.tfvars.template` to `terraform/terraform.tfvars`
2. Fill in your GCP project details
3. Run Jenkins pipeline: `create-pipeline`
4. Access entry service via outputted URL

## Services Communication Flow
```
User → Entry Service → API Service → Compute Service
                    ↓
                Storage/Database
```

## Cost
Designed to run within GCP free tier (~$0-10/month with $10 budget limit).

## Security
- Each service in isolated VPC
- Only API service can access resources
- Firewall rules restrict cross-service communication
