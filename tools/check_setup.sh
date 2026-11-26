#!/usr/bin/env bash
# Checks the accounts and tokens you created during the preparation (README).
#
#   tools/check_setup.sh
#
# It reads the TF_VAR_* variables (your Codespaces secrets), calls each API
# once, and tells you what is missing. It never prints the tokens.
set -uo pipefail

ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; failed=1; }
failed=0

echo "1. Variables"
# In the Codespace these come from your Codespaces secrets (see devcontainer.json).
for v in TF_VAR_github_repository TF_VAR_render_api_key TF_VAR_render_owner_id TF_VAR_grafana_stack_slug \
         TF_VAR_grafana_cloud_access_policy_token TF_VAR_grafana_service_account_token; do
  if [ -n "${!v:-}" ]; then ok "$v is set"; else bad "$v is not set"; fi
done
if [ -n "${TF_VAR_github_repository:-}" ] && [[ "$TF_VAR_github_repository" != */* ]]; then
  bad "TF_VAR_github_repository must look like <your-github-username>/se4ai-operations"
fi

echo "2. Render"
if [ -n "${TF_VAR_render_api_key:-}" ]; then
  owners=$(curl -s -H "Authorization: Bearer $TF_VAR_render_api_key" "https://api.render.com/v1/owners?limit=20")
  if echo "$owners" | jq -e 'type == "array"' >/dev/null 2>&1; then
    ok "API key works. Your workspaces (save the id as the Codespaces secret RENDER_OWNER_ID):"
    echo "$owners" | jq -r '.[].owner | "          \(.id)  \(.name)"'
    if [ -n "${TF_VAR_render_owner_id:-}" ] && ! echo "$owners" | jq -e --arg id "$TF_VAR_render_owner_id" 'any(.[]; .owner.id == $id)' >/dev/null; then
      bad "TF_VAR_render_owner_id is not one of these ids"
    fi
  else
    bad "Render did not accept the API key"
  fi
fi

echo "3. Grafana Cloud"
slug="${TF_VAR_grafana_stack_slug:-}"
if [ -n "$slug" ] && [ -n "${TF_VAR_grafana_cloud_access_policy_token:-}" ]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TF_VAR_grafana_cloud_access_policy_token" \
    "https://grafana.com/api/instances/$slug")
  if [ "$code" = 200 ]; then ok "access policy token can read stack '$slug'"
  else bad "access policy token cannot read stack '$slug' (HTTP $code): check the slug and the stacks:read scope"; fi
fi
if [ -n "$slug" ] && [ -n "${TF_VAR_grafana_service_account_token:-}" ]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TF_VAR_grafana_service_account_token" \
    "https://$slug.grafana.net/api/search?limit=1")
  if [ "$code" = 200 ]; then ok "service account token works on https://$slug.grafana.net"
  else bad "service account token rejected by https://$slug.grafana.net (HTTP $code)"; fi
fi

echo
if [ "$failed" = 0 ]; then echo "All set."; else echo "Fix the FAIL lines above, then run this again."; exit 1; fi
