# Each variable is read from the environment variable TF_VAR_<name>.
# In the Codespace, .devcontainer/devcontainer.json sets them from the
# Codespaces secrets you saved during the preparation. On your own machine, copy
# terraform.tfvars.example to terraform.tfvars and fill it in instead.

variable "render_api_key" {
  description = "Render API key (Account Settings > API Keys)."
  type        = string
  sensitive   = true
}

variable "render_owner_id" {
  description = "Your Render workspace ID, starts with tea- or usr- (tools/check_setup.sh prints it)."
  type        = string
}

variable "grafana_stack_slug" {
  description = "Name of your Grafana Cloud stack: the <slug> in https://<slug>.grafana.net."
  type        = string
}

variable "grafana_cloud_access_policy_token" {
  description = "Grafana Cloud access policy token (scopes: stacks:read, integration-management:read, integration-management:write)."
  type        = string
  sensitive   = true
}

variable "grafana_service_account_token" {
  description = "Service account token of your Grafana stack, role Editor (Administration > Service accounts)."
  type        = string
  sensitive   = true
}

variable "github_repository" {
  description = "Your fork, as <your-github-username>/se4ai-operations. CI pushes its image to ghcr.io/<this>."
  type        = string
}

variable "service_name" {
  description = "Name of the Render service. It becomes part of the public URL."
  type        = string
  default     = "spam-filter"
}

variable "region" {
  description = "Render region: frankfurt, ohio, oregon, singapore or virginia."
  type        = string
  default     = "singapore"
}
