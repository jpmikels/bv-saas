variable "project_id" { type = string }
variable "apis" { type = list(string) }
resource "google_project_service" "enabled" {
  for_each = toset(var.apis)
  project  = var.project_id
  service  = each.value
  disable_on_destroy = false
}
