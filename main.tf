provider "google" {
  project = "hacker2025-team-98-dev"
  region  = "us-central1"
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "aiplatform.googleapis.com",
    "bigquery.googleapis.com",
    "datastore.googleapis.com"
  ])
  
  project = "hacker2025-team-98-dev"
  service = each.value
}

# Storage bucket for Vertex AI
resource "google_storage_bucket" "staging" {
  name     = "trending-resolver-bucket"
  location = "us-central1"
  
  uniform_bucket_level_access = true
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "trending-resolver-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "trending-resolver-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.vpc.id
  region        = "us-central1"
}

# Cloud Run service for dashboard
resource "google_cloud_run_service" "resolver" {
  name     = "trending-resolver"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/hacker2025-team-98-dev/trending-resolver:latest"
        
        ports {
          container_port = 8501
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = "hacker2025-team-98-dev"
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to Cloud Run
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_service.resolver.name
  location = google_cloud_run_service.resolver.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output the service URL
output "dashboard_url" {
  value = google_cloud_run_service.resolver.status[0].url
}
