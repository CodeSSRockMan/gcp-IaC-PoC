#!/bin/bash
# Script to configure external Python app URL

COMPUTE_SERVICE_URL="https://your-compute-service-url"  # Replace with actual URL
EXTERNAL_APP_URL="https://your-external-app.com"       # Replace with your app URL

echo "🔗 Configuring external Python app..."
echo "External App URL: $EXTERNAL_APP_URL"

# Configure the proxy to point to your external app
curl -X POST "$COMPUTE_SERVICE_URL/load-app" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_url\": \"$EXTERNAL_APP_URL\",
    \"type\": \"proxy\"
  }"

echo ""
echo "✅ Configuration complete!"
echo "Your external app is now accessible at:"
echo "$COMPUTE_SERVICE_URL/external-app"
echo ""
echo "Or through the gateway at:"
echo "https://your-entry-service-url/app/external-app"
