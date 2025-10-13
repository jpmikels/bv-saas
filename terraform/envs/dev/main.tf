provider "google" {
  project = var.project_id
  region  = var.region
}

module "project" {
  source     = "../modules/project"
  project_id = var.project_id
  apis = [
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "documentai.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
  ]
}

module "artifact" {
  source      = "../modules/artifact"
  project_id  = var.project_id
  repo_name   = "containers"
  location    = var.region
}
