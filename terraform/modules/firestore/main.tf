// Firestore module: creates a Firestore database using free tier

resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

output "database_id" {
  value = google_firestore_database.default.name
}
