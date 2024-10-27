terraform {
  cloud {
    organization = "bikeSafeUMD"
    workspaces {
      name = "Bike-Safe-UMD"
    }
  }
  required_providers {
    railway = {
      source = "railway/railway"
      version = ">= 0.1.0"
    }
  }
}

provider "railway" {
  token = var.railway_api_token
}

resource "railway_project" "biking_app" {
  name = "UMD-Biking-App"
}

resource "railway_service" "web" {
  project_id = railway_project.biking_app.id
  name       = "web-service"
  start_cmd  = "python app.py"  # Adjust based on app entry point
}

output "project_id" {
  value = railway_project.biking_app.id
}
