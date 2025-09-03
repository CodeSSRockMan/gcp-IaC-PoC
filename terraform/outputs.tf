output "cloud_run_url" {
  value       = module.cloud_run.url
  description = "Cloud Run service URL"
}

output "cloud_run_entry_url" {
  value       = module.cloud_run_entry.url
  description = "Entry Service URL"
}

output "cloud_run_compute_url" {
  value       = module.cloud_run_compute.url
  description = "Compute Service URL"
}

output "cloud_run_api_url" {
  value       = module.cloud_run_api.url
  description = "API Service URL"
}

output "firestore_database_id" {
  value       = module.firestore.database_id
  description = "Firestore database ID"
}

output "swift_equivalent_bucket_name" {
  value       = google_storage_bucket.swift_equivalent.name
  description = "Cloud Storage bucket name (OpenStack Swift equivalent)"
}

output "neutron_network_id" {
  value       = module.neutron_network.vpc_id
  description = "VPC network ID (OpenStack Neutron equivalent)"
}

output "nova_compute_url" {
  value       = module.nova_compute.url
  description = "Cloud Run service URL (OpenStack Nova equivalent)"
}

output "cinder_equivalent_disk_name" {
  value       = google_compute_disk.cinder_equivalent.name
  description = "Persistent Disk name (OpenStack Cinder equivalent)"
}
