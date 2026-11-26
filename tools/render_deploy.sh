#!/usr/bin/env bash
# Deploys one image to the Render service and waits until it is live.
#
#   RENDER_API_KEY=... RENDER_SERVICE_ID=srv-... tools/render_deploy.sh ghcr.io/<you>/se4ai-operations:<commit>
#
# Uses the Render API: POST /v1/services/{id}/deploys starts a deploy of the
# given image; GET /v1/services/{id}/deploys/{deployId} tells us how it went.
set -euo pipefail

image="${1:?usage: render_deploy.sh <image-url>}"
: "${RENDER_API_KEY:?RENDER_API_KEY is not set}"
: "${RENDER_SERVICE_ID:?RENDER_SERVICE_ID is not set}"
api="https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys"

echo "Deploying $image"
deploy_id=$(curl --fail-with-body --silent --show-error -X POST "$api" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"imageUrl\": \"$image\"}" | jq -r .id)
echo "Render deploy $deploy_id started"

for _ in $(seq 1 60); do   # at most 10 minutes
  sleep 10
  status=$(curl --fail-with-body --silent --show-error "$api/$deploy_id" \
    -H "Authorization: Bearer $RENDER_API_KEY" | jq -r .status)
  echo "  status: $status"
  case "$status" in
    live) echo "Deploy is live."; exit 0 ;;
    *failed|canceled|deactivated) echo "Deploy did not go live: $status" >&2; exit 1 ;;
  esac
done
echo "Timed out waiting for the deploy." >&2
exit 1
