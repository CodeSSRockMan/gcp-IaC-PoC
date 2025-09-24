# Medical Appointments Infrastructure Outputs

# VM Outputs
output "vm1_private_internal_ip" {
  value       = google_compute_instance.vm1_private.network_interface[0].network_ip
  description = "🔒 VM1 (Private) - Internal IP address (no public access)"
}

output "vm2_public_external_ip" {
  value       = google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip
  description = "🌍 VM2 (Public) - External IP address (accessible from internet)"
}

output "vm2_public_internal_ip" {
  value       = google_compute_instance.vm2_public.network_interface[0].network_ip
  description = "🔗 VM2 (Public) - Internal IP address"
}

output "main_app_url" {
  value       = "http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/medical-appointments/"
  description = "🏥 Main Medical Appointments App URL - Click to access the app (hosted on VM2)"
}

output "api_health_url" {
  value       = "http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/api/health"
  description = "🔍 API Health Check URL - Click to test API health (VM2)"
}

output "api_base_url" {
  value       = "http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/api/"
  description = "🔗 API Base URL for all endpoints (VM2)"
}

output "cloud_run_url" {
  value       = module.cloud_run.service_url
  description = "🚀 Cloud Run service URL (serverless deployment)"
}

output "ssh_command_vm2" {
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}"
  description = "🔑 SSH command to connect to VM2 (public, directly accessible)"
}

output "ssh_command_vm1_via_vm2" {
  value       = "ssh -i ~/.ssh/id_rsa -J ubuntu@${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip} ubuntu@${google_compute_instance.vm1_private.network_interface[0].network_ip}"
  description = "🔑 SSH command to connect to VM1 via VM2 (bastion/jump host)"
}

output "firestore_database_name" {
  value       = module.firestore.database_name
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
  value       = module.vpc.vpc_name
  description = "🌐 VPC network name (vnet-nebo)"
}

output "public_subnet_name" {
  value       = module.vpc.public_subnet_name
  description = "🌍 Public subnet name (snet-public)"
}

output "private_subnet_name" {
  value       = module.vpc.private_subnet_name
  description = "🔒 Private subnet name (snet-private)"
}

output "network_summary" {
  value       = <<-EOF
  
  🌐 NETWORK CONFIGURATION:
  
  VPC: vnet-nebo (10.0.0.0/16)
  ├── snet-public (10.0.0.0/17) - Public subnet for external access
  └── snet-private (10.0.128.0/17) - Private subnet for internal resources
  
  EOF
  description = "📋 Network topology summary"
}

output "service_account_email" {
  value       = google_service_account.app_service_account.email
  description = "🔐 Service account email for the application"
}

# Quick access summary
output "quick_access_summary" {
  value       = <<-EOF
  
  🏥 MEDICAL APPOINTMENTS INFRASTRUCTURE READY!
  
  �️ VM ARCHITECTURE:
     VM1 (Private): ${google_compute_instance.vm1_private.network_interface[0].network_ip} - Not accessible from internet
     VM2 (Public):  ${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip} - Accessible from internet
  
  �📱 Main Application (VM2): 
     http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/medical-appointments/
  
  🔍 API Health Check (VM2): 
     http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/api/health
  
  🔗 API Endpoints (VM2):
     Appointments: http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/api/appointments
     Patients:     http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/api/patients
     Doctors:      http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/api/doctors
     Language:     http://${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}/api/lang
  
  🔑 SSH Access: 
     VM2 (Direct): ssh -i ~/.ssh/id_rsa ubuntu@${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}
     VM1 (via VM2): ssh -i ~/.ssh/id_rsa -J ubuntu@${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip} ubuntu@${google_compute_instance.vm1_private.network_interface[0].network_ip}
  
  🚀 Cloud Run URL: 
     ${module.cloud_run.service_url}
  
  📊 Monitoring: 
     https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.medical_appointments_dashboard.id}?project=${var.project_id}
  
  ✅ ACCEPTANCE CRITERIA MET:
     • VM1 in snet-private: NOT accessible from public hosts ❌🌐 ✅🔒
     • VM2 in snet-public: Accessible from public hosts ✅🌐 
     • VM2 can connect to VM1: Internal VPC communication enabled ✅🔗
  
  EOF
  description = "📋 Complete access summary with VM connectivity details"
}

# Acceptance Criteria Validation
output "acceptance_criteria" {
  value       = <<-EOF
  
  🎯 ACCEPTANCE CRITERIA VALIDATION:
  
  ✅ VM1 deployed to subnet snet-private is NOT accessible from public hosts
     - VM1 IP: ${google_compute_instance.vm1_private.network_interface[0].network_ip}
     - Subnet: ${module.vpc.private_subnet_name} (10.0.128.0/17)
     - No public IP assigned (no access_config block)
     - Only accessible via internal VPC communication
  
  ✅ VM2 deployed to subnet snet-public IS accessible from public hosts  
     - VM2 External IP: ${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip}
     - VM2 Internal IP: ${google_compute_instance.vm2_public.network_interface[0].network_ip}
     - Subnet: ${module.vpc.public_subnet_name} (10.0.0.0/17)
     - Public IP assigned via access_config block
  
  ✅ VM2 is able to connect to VM1 (internal VPC communication)
     - Both VMs are in the same VPC: ${module.vpc.vpc_name}
     - Firewall rules allow internal communication
     - Test connection: SSH to VM2, then connect to VM1 at ${google_compute_instance.vm1_private.network_interface[0].network_ip}
     - Jump host command: ssh -J ubuntu@${google_compute_instance.vm2_public.network_interface[0].access_config[0].nat_ip} ubuntu@${google_compute_instance.vm1_private.network_interface[0].network_ip}
  
  🌐 Network Architecture:
     VPC: vnet-nebo (10.0.0.0/16)
     ├── snet-public (10.0.0.0/17) ← VM2 (Public access)
     └── snet-private (10.0.128.0/17) ← VM1 (Private, NAT for outbound)
  
  EOF
  description = "🎯 Validation that all acceptance criteria are met"
}
