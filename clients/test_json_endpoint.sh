#!/bin/bash
# Test JSON endpoint using curl

echo "Testing JSON endpoint..."
echo ""

curl -X POST "http://127.0.0.1:8000/json/user" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Wallace",
    "email": "wallace@example.com",
    "is_active": true
  }' | jq .

echo ""
echo "✅ JSON endpoint test complete"
