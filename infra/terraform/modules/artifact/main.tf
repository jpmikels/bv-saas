variable "project_id" { type = string }
variable "repo_name"  { type = string }
variable "location"   { type = string }
resource "google_artifact_registry_repository" "repo" {
  location      = var.location
  repository_id = var.repo_name
  format        = "DOCKER"
  project       = var.project_id
}
