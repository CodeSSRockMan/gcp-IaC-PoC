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
}

variable "cloud_run_image" {
  description = "Cloud Run container image"
  type        = string
}

variable "entry_image" {
  description = "Entry service container image"
  type        = string
}

variable "compute_image" {
  description = "Compute service container image"
  type        = string
}

variable "api_image" {
  description = "API service container image"
  type        = string
}

variable "nova_image" {
  description = "Nova compute container image"
  type        = string
}
