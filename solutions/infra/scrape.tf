# Task 3: collect the telemetry.
#
# Grafana Cloud's "Metrics Endpoint" integration downloads (scrapes) the
# service's /metrics page every minute and stores the numbers, so the
# dashboard can query them. This is the pull model, like Prometheus.

resource "grafana_connections_metrics_endpoint_scrape_job" "app" {
  provider                = grafana.connections
  stack_id                = data.grafana_cloud_stack.this.id
  name                    = "spam-filter"
  enabled                 = true
  scrape_interval_seconds = 60

  # The full https:// URL of the metrics page of your Render service.
  url = "${render_web_service.app.url}/metrics"

  # app/main.py expects "Authorization: Bearer <token>".
  authentication_method       = "bearer"
  authentication_bearer_token = random_password.metrics_token.result
}
