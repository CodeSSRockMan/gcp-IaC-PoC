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

# Firewall rules
resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-access"]
}

resource "google_compute_firewall" "allow_http" {
  name    = "allow-http"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "8080", "5000"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-access"]
}

# Firestore Database
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# Storage bucket for app deployments
resource "google_storage_bucket" "app_storage" {
  name     = "${var.project_id}-medical-apps"
  location = var.region
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Service Account for applications
resource "google_service_account" "app_service_account" {
  account_id   = "medical-appointments-sa"
  display_name = "Medical Appointments Service Account"
}

resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

resource "google_project_iam_member" "monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Compute Instance for hosting applications
resource "google_compute_instance" "app_instance" {
  name         = "medical-appointments-instance"
  machine_type = "e2-micro" # Free tier eligible
  zone         = var.zone

  tags = ["ssh-access", "http-access"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 20
      type  = "pd-standard"
    }
  }

  network_interface {
    network    = google_compute_network.vpc.id
    subnetwork = google_compute_subnetwork.subnet.id
    
    access_config {
      # Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "ubuntu:${var.ssh_key}"
  }

  metadata_startup_script = file("${path.module}/startup-script.sh")

  service_account {
    email  = google_service_account.app_service_account.email
    scopes = ["cloud-platform"]
  }
}

# Cloud Run service for the medical appointments app
resource "google_cloud_run_service" "medical_appointments" {
  name     = "medical-appointments-api"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
    
    spec {
      containers {
        image = "gcr.io/${var.project_id}/medical-appointments:latest"
        
        ports {
          container_port = 8080
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }
      
      service_account_name = google_service_account.app_service_account.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_firestore_database.database]
}

# Allow unauthenticated access to Cloud Run
resource "google_cloud_run_service_iam_member" "allow_unauthenticated" {
  service  = google_cloud_run_service.medical_appointments.name
  location = google_cloud_run_service.medical_appointments.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Monitoring notification channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification Channel"
  type         = "email"
  labels = {
    email_address = "admin@example.com" # Change this to your email
  }
}

# Cloud Monitoring alerts for the instance
resource "google_monitoring_alert_policy" "high_cpu" {
  display_name = "High CPU Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "VM Instance - CPU utilization"
    
    condition_threshold {
      filter         = "resource.type=\"gce_instance\""
      comparison     = "COMPARISON_GT"
      threshold_value = 0.8
      duration       = "300s"
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.id]
}

resource "google_monitoring_alert_policy" "high_memory" {
  display_name = "High Memory Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "VM Instance - Memory utilization"
    
    condition_threshold {
      filter         = "resource.type=\"gce_instance\""
      comparison     = "COMPARISON_GT"
      threshold_value = 0.8
      duration       = "300s"
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Webhooks for automated deployments
resource "google_cloudbuild_trigger" "app_deployment" {
  name        = "medical-appointments-deployment"
  description = "Trigger for medical appointments app deployment"

  github {
    owner = "your-github-username" # Change this
    name  = "your-repo-name"       # Change this
    push {
      branch = "main"
    }
  }

  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build",
        "-t", "gcr.io/${var.project_id}/medical-appointments:$COMMIT_SHA",
        "-t", "gcr.io/${var.project_id}/medical-appointments:latest",
        "./apps/medical-appointments"
      ]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${var.project_id}/medical-appointments:$COMMIT_SHA"]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${var.project_id}/medical-appointments:latest"]
    }

    step {
      name = "gcr.io/cloud-builders/gcloud"
      args = [
        "run", "deploy", "medical-appointments-api",
        "--image", "gcr.io/${var.project_id}/medical-appointments:$COMMIT_SHA",
        "--region", var.region,
        "--platform", "managed"
      ]
    }
  }
}
