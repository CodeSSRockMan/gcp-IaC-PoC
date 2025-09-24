variable "name" {
  description = "Cloud Run service name"
  type        = string
}

variable "image" {
  description = "Container image for Cloud Run"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run"
  type        = string
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "service_account_email" {
  description = "Service account email to use"
  type        = string
}
