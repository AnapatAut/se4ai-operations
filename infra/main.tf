# The infrastructure of the spam-filter service, as code.
#
#   render_web_service.app              the service, on Render's free plan
#   random_password.metrics_token       a secret shared by the service and Grafana Cloud
#   grafana_dashboard.spam_filter       the dashboard, defined in dashboard.json
#   (scrape.tf)                         Grafana Cloud collecting /metrics: Task 3

# ---------------------------------------------------------------- providers --

provider "render" {
  api_key                    = var.render_api_key
  owner_id                   = var.render_owner_id
  wait_for_deploy_completion = true
}

# Grafana Cloud has three APIs, so we configure the provider three times:
# the Cloud API (look up the stack), the Connections API (scrape jobs), and the
# stack's own Grafana (dashboards).
provider "grafana" {
  alias                     = "cloud"
  cloud_access_policy_token = var.grafana_cloud_access_policy_token
}

data "grafana_cloud_stack" "this" {
  provider = grafana.cloud
  slug     = var.grafana_stack_slug
}

provider "grafana" {
  alias                        = "connections"
  connections_api_url          = data.grafana_cloud_stack.this.connections_api_url
  connections_api_access_token = var.grafana_cloud_access_policy_token
}

provider "grafana" {
  url  = "https://${var.grafana_stack_slug}.grafana.net"
  auth = var.grafana_service_account_token
}

# ------------------------------------------------------------------ service --

resource "random_password" "metrics_token" {
  length  = 32
  special = false
}

resource "render_web_service" "app" {
  name              = var.service_name
  plan              = "free"
  region            = var.region
  health_check_path = "/health"

  runtime_source = {
    image = {
      image_url = lower("ghcr.io/${var.github_repository}") # image names are lower case
      tag       = "latest"
    }
  }

  env_vars = {
    METRICS_TOKEN = { value = random_password.metrics_token.result }
  }

  lifecycle {
    # Terraform creates the service once. After that, CI/CD deploys each new
    # image through the Render API, so Terraform must not undo those deploys.
    # (Also: the Render provider cannot update free-plan services, see README.)
    ignore_changes = [runtime_source]
  }
}

# ---------------------------------------------------------------- dashboard --

resource "grafana_dashboard" "spam_filter" {
  config_json = file("${path.module}/dashboard.json")
  overwrite   = true
}
