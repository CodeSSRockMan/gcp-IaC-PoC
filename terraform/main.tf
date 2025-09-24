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

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  vpc_name            = "vnet-nebo"
  public_subnet_name  = "snet-public"
  private_subnet_name = "snet-private"
  public_subnet_cidr  = "10.0.0.0/17"
  private_subnet_cidr = "10.0.128.0/17"
  region              = var.region
}

# Firestore Module
module "firestore" {
  source = "./modules/firestore"

  project_id = var.project_id
  region     = var.region
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

# VM1 - Private subnet instance (not accessible from public hosts)
resource "google_compute_instance" "vm1_private" {
  name         = "vm1-private-instance"
  machine_type = "e2-micro" # Free tier eligible
  zone         = var.zone

  tags = ["ssh-access", "private-vm"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 20
      type  = "pd-standard"
    }
  }

  network_interface {
    network    = module.vpc.vpc_id
    subnetwork = module.vpc.private_subnet_id
    # No access_config = No public IP (not accessible from internet)
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

# VM2 - Public subnet instance (accessible from public hosts)
resource "google_compute_instance" "vm2_public" {
  name         = "vm2-public-instance"
  machine_type = "e2-micro" # Free tier eligible
  zone         = var.zone

  tags = ["ssh-access", "http-access", "public-vm"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 20
      type  = "pd-standard"
    }
  }

  network_interface {
    network    = module.vpc.vpc_id
    subnetwork = module.vpc.public_subnet_id

    access_config {
      # Ephemeral public IP (accessible from internet)
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

# Cloud Run Module
module "cloud_run" {
  source = "./modules/cloud_run"

  name                  = "medical-appointments-api"
  image                 = "gcr.io/${var.project_id}/medical-appointments:latest"
  region                = var.region
  project_id            = var.project_id
  service_account_email = google_service_account.app_service_account.email

  depends_on = [module.firestore]
}

# Cloud Monitoring notification channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "Medical Appointments Admin"
  type         = "email"
  labels = {
    email_address = "admin@example.com" # Update with your email
  }
}

# CPU Utilization Alert
resource "google_monitoring_alert_policy" "high_cpu" {
  display_name = "High CPU Usage Alert"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "VM Instance - CPU utilization > 80%"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND resource.labels.instance_id=\"${google_compute_instance.vm2_public.instance_id}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      duration        = "300s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Memory Utilization Alert
resource "google_monitoring_alert_policy" "high_memory" {
  display_name = "High Memory Usage Alert"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "VM Instance - Memory utilization > 85%"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND resource.labels.instance_id=\"${google_compute_instance.vm2_public.instance_id}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.85
      duration        = "300s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Disk I/O Alert
resource "google_monitoring_alert_policy" "high_disk_io" {
  display_name = "High Disk I/O Alert"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "VM Instance - Disk Read Operations > 1000/min"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND resource.labels.instance_id=\"${google_compute_instance.vm2_public.instance_id}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 1000
      duration        = "300s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Network Throughput Alert
resource "google_monitoring_alert_policy" "high_network" {
  display_name = "High Network Throughput Alert"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "VM Instance - Network sent bytes > 100MB/min"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND resource.labels.instance_id=\"${google_compute_instance.vm2_public.instance_id}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 104857600 # 100MB in bytes
      duration        = "300s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Monitoring Dashboard
resource "google_monitoring_dashboard" "medical_appointments_dashboard" {
  dashboard_json = jsonencode({
    displayName = "Medical Appointments Infrastructure"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "CPU Utilization"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"gce_instance\" AND resource.labels.instance_id=\"${google_compute_instance.vm2_public.instance_id}\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
              }]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Memory Usage"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"gce_instance\" AND resource.labels.instance_id=\"${google_compute_instance.vm2_public.instance_id}\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
              }]
            }
          }
        }
      ]
    }
  })
}

# Webhooks for automated deployments
resource "google_cloudbuild_trigger" "app_deployment" {
  name        = "medical-appointments-deployment"
  description = "Trigger for medical appointments app deployment"

  github {
    owner = "CodeSSRockMan" # Updated to match your GitHub
    name  = "gcp-IaC-PoC"   # Updated to match your repo
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
