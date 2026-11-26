output "app_url" {
  description = "Public URL of the service. Save it as the APP_URL repository variable."
  value       = render_web_service.app.url
}

output "render_service_id" {
  description = "ID of the Render service. Save it as the RENDER_SERVICE_ID repository variable."
  value       = render_web_service.app.id
}

output "dashboard_url" {
  description = "The spam-filter dashboard in Grafana Cloud."
  value       = grafana_dashboard.spam_filter.url
}

output "metrics_token" {
  description = "Token that /metrics expects. Show it with: terraform output -raw metrics_token"
  value       = random_password.metrics_token.result
  sensitive   = true
}
