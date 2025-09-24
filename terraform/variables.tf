variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region (use us-central1 for free tier)"
  type        = string
  default     = "us-central1"
}

variable "billing_account_id" {
  description = "GCP Billing Account ID for budget"
  type        = string
}

variable "cloud_run_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "medical-appointments-api"
}

variable "cloud_run_image" {
  description = "Cloud Run container image"
  type        = string
  default     = "gcr.io/peaceful-oath-470112-e8/medical-appointments:latest"
}

variable "entry_image" {
  description = "Entry service container image"
  type        = string
  default     = "gcr.io/peaceful-oath-470112-e8/entry-service:latest"
}

variable "compute_image" {
  description = "Compute service container image"
  type        = string
  default     = "gcr.io/peaceful-oath-470112-e8/compute-service:latest"
}

variable "api_image" {
  description = "API service container image"
  type        = string
  default     = "gcr.io/peaceful-oath-470112-e8/api-service:latest"
}

variable "nova_image" {
  description = "Nova compute container image"
  type        = string
  default     = "gcr.io/peaceful-oath-470112-e8/nova-service:latest"
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
