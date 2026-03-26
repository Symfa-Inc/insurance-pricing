#!/bin/sh
set -e

# Replace the default API base URL in built assets when API_URL is provided at runtime.
if [ -n "$API_URL" ]; then
  ESCAPED=$(echo "$API_URL" | sed 's/&/\\&/g')
  find /app -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i "s|http://localhost:8000|$ESCAPED|g" {} \;
fi

exec "$@"
