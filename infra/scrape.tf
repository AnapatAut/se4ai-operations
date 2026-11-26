# Task 3: collect the telemetry.
#
# Grafana Cloud's "Metrics Endpoint" integration downloads (scrapes) the
# service's /metrics page every minute and stores the numbers, so the
# dashboard can query them. This is the pull model, like Prometheus.
#
# TODO Task 3: uncomment the resource below (select the lines, then Ctrl+/ or
# Cmd+/) and replace the three ??? . Look at main.tf: the values you need are
# attributes of resources defined there.
#
# resource "grafana_connections_metrics_endpoint_scrape_job" "app" {
#   provider                = grafana.connections
#   stack_id                = data.grafana_cloud_stack.this.id
#   name                    = "spam-filter"
#   enabled                 = true
#   scrape_interval_seconds = 60
#
#   # The full https:// URL of the metrics page of your Render service.
#   url = ???
#
#   # How app/main.py checks who may read /metrics: "basic" or "bearer"?
#   authentication_method       = ???
#   authentication_bearer_token = ???
# }
