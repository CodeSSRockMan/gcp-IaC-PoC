# Terraform Configuration

## Files Structure
```
terraform/
├── main.tf              # Main infrastructure
├── variables.tf         # Input variables
├── outputs.tf           # Output values  
├── budget.tf            # Cost management
├── terraform.tfvars     # Variable values (create from template)
└── modules/             # Reusable modules
    ├── vpc/
    ├── cloud_run/
    └── firestore/
```

## Variables
Copy `terraform.tfvars.template` to `terraform.tfvars` and configure:
- `project_id`: Your GCP project ID
- `billing_account_id`: Your billing account ID
- Container images for each service

## Resources Created
- 4 VPCs (entry, compute, api, neutron)
- 4 Cloud Run services (OpenStack equivalents)
- Cloud Storage bucket (Swift equivalent)
- Firestore database
- Budget alerts ($10 limit)
