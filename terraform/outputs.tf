# Medical Appointments Infrastructure Outputs

output "instance_external_ip" {
  value       = google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip
  description = "External IP address of the compute instance"
}

output "main_app_url" {
  value       = "http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/medical-appointments/"
  description = "🏥 Main Medical Appointments App URL - Click to access the app"
}

output "api_health_url" {
  value       = "http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/api/health"
  description = "🔍 API Health Check URL - Click to test API health"
}

output "api_base_url" {
  value       = "http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/api/"
  description = "🔗 API Base URL for all endpoints"
}

output "cloud_run_url" {
  value       = google_cloud_run_service.medical_appointments.status[0].url
  description = "🚀 Cloud Run service URL (serverless deployment)"
}

output "ssh_command" {
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}"
  description = "🔑 SSH command to connect to the instance"
}

output "firestore_database_name" {
  value       = google_firestore_database.database.name
  description = "🔥 Firestore database name"
}

output "storage_bucket_name" {
  value       = google_storage_bucket.app_storage.name
  description = "📦 Storage bucket name for app deployments"
}

output "monitoring_dashboard_url" {
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.medical_appointments_dashboard.id}?project=${var.project_id}"
  description = "📊 Cloud Monitoring Dashboard URL"
}

output "vpc_network_name" {
  value       = google_compute_network.vpc.name
  description = "🌐 VPC network name"
}

output "service_account_email" {
  value       = google_service_account.app_service_account.email
  description = "🔐 Service account email for the application"
}

# Quick access summary
output "quick_access_summary" {
  value = <<-EOF
  
  🏥 MEDICAL APPOINTMENTS INFRASTRUCTURE READY!
  
  📱 Main Application: 
     http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/medical-appointments/
  
  🔍 API Health Check: 
     http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/api/health
  
  🔗 API Endpoints:
     Appointments: http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/api/appointments
     Patients:     http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/api/patients
     Doctors:      http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/api/doctors
     Language:     http://${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}/api/lang
  
  🔑 SSH Access: 
     ssh -i ~/.ssh/id_rsa ubuntu@${google_compute_instance.app_instance.network_interface[0].access_config[0].nat_ip}
  
  🚀 Cloud Run URL: 
     ${google_cloud_run_service.medical_appointments.status[0].url}
  
  📊 Monitoring: 
     https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.medical_appointments_dashboard.id}?project=${var.project_id}
  
  EOF
  description = "📋 Complete access summary with clickable links"
}
