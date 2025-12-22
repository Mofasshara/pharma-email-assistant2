#!/usr/bin/env bash
set -e

BASE_URL="https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net"

curl -i -X POST \
  "$BASE_URL/banking/rewrite" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "This investment guarantees high returns with minimal risk.",
    "audience": "client",
    "language": "en"
  }'
