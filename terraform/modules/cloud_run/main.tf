// Cloud Run module: deploys a service using free tier options

resource "google_cloud_run_service" "app" {
  name     = var.name
  location = var.region

  template {
    spec {
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
