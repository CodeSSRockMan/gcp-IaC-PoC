output "cloud_run_url" {
  value       = google_cloud_run_service.free_api.status[0].url
  description = "Cloud Run service URL"
}

output "storage_bucket" {
  value       = google_storage_bucket.free_storage.name
  description = "Storage bucket name"
}

output "monthly_cost" {
  value       = "$0.00 - All within free tier limits!"
  description = "Estimated monthly cost"
}
