// Cloud Run module: deploys a service with auto-scaling capabilities

resource "google_cloud_run_service" "app" {
  name     = var.name
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"    # Scale to zero when no traffic
        "autoscaling.knative.dev/maxScale" = "10"   # Maximum 10 instances (free tier friendly)
        "run.googleapis.com/cpu-throttling" = "true" # Enable CPU throttling for cost efficiency
      }
    }
    spec {
      container_concurrency = 100  # Allow up to 100 concurrent requests per instance
      containers {
        image = var.image
        resources {
          limits = {
            cpu    = "1000m"   // 1 vCPU (free tier limit)
            memory = "512Mi"   // 512MiB (well within free tier)
          }
        }
        env {
          name  = "FIRESTORE_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
        env {
          name  = "AUTO_SCALE_ENABLED"
          value = "true"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "public_invoker" {
  service  = google_cloud_run_service.app.name
  location = google_cloud_run_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "url" {
  value = google_cloud_run_service.app.status[0].url
}
