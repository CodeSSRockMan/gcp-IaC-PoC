// VPC module: creates a VPC and a private subnet for app resources

resource "google_compute_network" "vpc_network" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "private_subnet" {
  name                     = var.subnet_name
  ip_cidr_range            = var.subnet_cidr
  region                   = var.region
  network                  = google_compute_network.vpc_network.id
  private_ip_google_access = true
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-access"]
}

# Allow only API service to access resources (example: allow HTTP from API subnet)
resource "google_compute_firewall" "allow_api_to_resource" {
  name    = "allow-api-to-resource"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"] # Adjust as needed
  }

  source_ranges = [var.api_subnet_cidr] # Pass API subnet CIDR as a variable
  target_tags   = ["resource-access"]
}

# Deny all other ingress except SSH and API
resource "google_compute_firewall" "deny_all_ingress" {
  name    = "deny-all-ingress"
  network = google_compute_network.vpc_network.name

  deny {
    protocol = "all"
  }

  priority      = 65534
  source_ranges = ["0.0.0.0/0"]
}

output "vpc_id" {
  value = google_compute_network.vpc_network.id
}

output "subnet_id" {
  value = google_compute_subnetwork.private_subnet.id
}
