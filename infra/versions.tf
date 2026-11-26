terraform {
  required_version = ">= 1.5"

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.9"
    }
    grafana = {
      source  = "grafana/grafana"
      version = "~> 4.55"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
