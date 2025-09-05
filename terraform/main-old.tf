# Main Terraform configuration for Medical Appointments Infrastructure

terraform {
  required_version = ">= 0.14"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "ssh_key" {
  description = "SSH public key for instance access"
  type        = string
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "medical-appointments-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "medical-appointments-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}
  location = var.region
  force_destroy = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "cloud_run_swift_access" {
  bucket = google_storage_bucket.swift_equivalent.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_cloud_scheduler_job" "daily_app_trigger" {
  name             = "run-app-daily"
  description      = "Trigger Cloud Run app once per day"
  schedule         = "0 3 * * *" # 3:00 AM UTC daily
  time_zone        = "Etc/UTC"

  http_target {
    http_method = "GET"
    uri         = module.cloud_run.url
    oidc_token {
      service_account_email = google_service_account.cloud_run_sa.email
    }
  }
}

# Scheduler to start instances (example, adjust as needed)
resource "google_cloud_scheduler_job" "start_instances" {
  name        = "start-instances-daily"
  description = "Start instances every day at 4:00 AM UTC"
  schedule    = "0 4 * * *"
  time_zone   = "Etc/UTC"

  http_target {
    http_method = "POST"
    uri         = "https://compute.googleapis.com/compute/v1/projects/${var.project_id}/zones/${var.region}-a/instances/start"
    oidc_token {
      service_account_email = google_service_account.cloud_run_sa.email
    }
    headers = {
      "Content-Type" = "application/json"
    }
    body = jsonencode({
      # Add instance names or other parameters as needed
    })
  }
}

# Entry Service VPC
module "vpc_entry" {
  source      = "./modules/vpc"
  vpc_name    = "entry-vpc"
  subnet_name = "entry-subnet"
  subnet_cidr = "10.10.1.0/24"
  region      = var.region
}

# Compute Service VPC
module "vpc_compute" {
  source      = "./modules/vpc"
  vpc_name    = "compute-vpc"
  subnet_name = "compute-subnet"
  subnet_cidr = "10.20.1.0/24"
  region      = var.region
}

# API Service VPC
module "vpc_api" {
  source      = "./modules/vpc"
  vpc_name    = "api-vpc"
  subnet_name = "api-subnet"
  subnet_cidr = "10.30.1.0/24"
  region      = var.region
}

# Entry Cloud Run
module "cloud_run_entry" {
  source      = "./modules/cloud_run"
  region      = var.region
  subnet_id   = module.vpc_entry.subnet_id
  name        = "entry-service"
  image       = var.entry_image
  project_id  = var.project_id
  service_account_email = google_service_account.cloud_run_sa.email
}

# Compute Cloud Run
module "cloud_run_compute" {
  source      = "./modules/cloud_run"
  region      = var.region
  subnet_id   = module.vpc_compute.subnet_id
  name        = "compute-service"
  image       = var.compute_image
  project_id  = var.project_id
  service_account_email = google_service_account.cloud_run_sa.email
}

# API Cloud Run (the only one with access to resources)
module "cloud_run_api" {
  source      = "./modules/cloud_run"
  region      = var.region
  subnet_id   = module.vpc_api.subnet_id
  name        = "api-service"
  image       = var.api_image
  project_id  = var.project_id
  service_account_email = google_service_account.cloud_run_sa.email
}

# Only allow API service to access resources (firewall rules would be in each VPC module)

# OpenStack Neutron equivalent (Networking)
module "neutron_network" {
  source      = "./modules/vpc"
  vpc_name    = "neutron-network"
  subnet_name = "neutron-subnet"
  subnet_cidr = "10.40.1.0/24"
  region      = var.region
  api_subnet_cidr = module.vpc_api.subnet_id # or the correct CIDR
}

# OpenStack Nova equivalent (Compute)
module "nova_compute" {
  source      = "./modules/cloud_run"
  region      = var.region
  subnet_id   = module.neutron_network.subnet_id
  name        = "nova-compute"
  image       = var.nova_image
  project_id  = var.project_id
  service_account_email = google_service_account.cloud_run_sa.email
}

# OpenStack Cinder equivalent (Block Storage)
resource "google_compute_disk" "cinder_equivalent" {
  name  = "cinder-equivalent"
  type  = "pd-standard"
  zone  = "${var.region}-a"
  size  = 10 # 10GB
}

# Only allow API service to access resources (firewall rules would be in each VPC module)
