#!/bin/bash
# Quick Demo Script for Medical Appointments API

echo "🏥 Medical Appointments API - Quick Demo"
echo "========================================"

BASE_URL="http://localhost:8081"

echo "1. Testing Health Endpoint:"
curl -s "$BASE_URL/health" | jq .

echo -e "\n2. Testing API Health:"
curl -s "$BASE_URL/api/health" | jq .

echo -e "\n3. Testing Language Endpoint (was previously broken):"
curl -s "$BASE_URL/api/lang" | jq .

echo -e "\n4. Testing Appointments (Firebase not available locally):"
curl -s "$BASE_URL/api/appointments" | jq .

echo -e "\n5. Testing Main App Page (first 5 lines):"
curl -s "$BASE_URL/medical-appointments/" | head -n 5

echo -e "\n6. Testing Interactive Dashboard (first 5 lines):"
curl -s "$BASE_URL/" | head -n 5

echo -e "\n✅ Demo Complete!"
echo "🌐 View interactive dashboard: $BASE_URL/"
echo "📖 View API docs: $BASE_URL/api/"
