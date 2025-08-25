// main Terraform configuration

variable "region" {
  description = "GCP region (use us-central1 for free tier)"
  type        = string
  default     = "us-central1"
}

module "vpc" {
  source      = "./modules/vpc"
  vpc_name    = "app-vpc"
  subnet_name = "app-subnet"
  subnet_cidr = "10.0.1.0/24"
  region      = var.region
}

module "cloud_run" {
  source      = "./modules/cloud_run"
  region      = var.region
  subnet_id   = module.vpc.subnet_id
}

module "firestore" {
  source      = "./modules/firestore"
  region      = var.region
}

output "cloud_run_url" {
  value       = module.cloud_run.url
  description = "Cloud Run service URL"
}

output "firestore_database_id" {
  value       = module.firestore.database_id
  description = "Firestore database ID"
}
