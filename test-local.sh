#!/bin/bash
# Local Development Test Script
# This script helps test the services locally before deploying to GCP

echo "🚀 Python App Local Development Test"
echo "===================================="

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import flask, requests" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip3 install flask requests google-cloud-firestore google-cloud-storage
fi

echo "✅ Dependencies ready"

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local script_path=$3
    
    echo "🔧 Starting $service_name on port $port..."
    export PORT=$port
    python3 "$script_path" &
    local pid=$!
    echo "$pid" > "/tmp/${service_name}.pid"
    echo "   PID: $pid"
    sleep 2
}

# Function to check service health
check_health() {
    local service_name=$1
    local port=$2
    
    echo "🩺 Checking $service_name health..."
    if curl -s "http://localhost:$port/health" > /dev/null; then
        echo "   ✅ $service_name is healthy"
        return 0
    else
        echo "   ❌ $service_name is not responding"
        return 1
    fi
}

# Stop any existing services
echo "🧹 Cleaning up existing processes..."
pkill -f "python3.*service\.py" 2>/dev/null || true
rm -f /tmp/*.pid

# Start services
echo ""
echo "🚀 Starting services..."
start_service "compute" 8080 "services/compute-service.py"
start_service "api" 8081 "services/api-service.py"
start_service "entry" 8082 "services/entry-service.py"

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service health
echo ""
echo "🔍 Health checks..."
compute_ok=false
api_ok=false
entry_ok=false

if check_health "compute" 8080; then compute_ok=true; fi
if check_health "api" 8081; then api_ok=true; fi
if check_health "entry" 8082; then entry_ok=true; fi

echo ""
if [ "$compute_ok" = true ] && [ "$api_ok" = true ] && [ "$entry_ok" = true ]; then
    echo "🎉 All services are running!"
    echo ""
    echo "🌐 Access points:"
    echo "   • Main App:      http://localhost:8082/app"
    echo "   • Gateway:       http://localhost:8082"
    echo "   • System Status: http://localhost:8082/status"
    echo "   • Shell Access:  http://localhost:8082/shell"
    echo "   • API Status:    http://localhost:8082/api/status"
    echo ""
    echo "📊 Direct service access:"
    echo "   • Compute:       http://localhost:8080"
    echo "   • API:           http://localhost:8081"
    echo "   • Entry:         http://localhost:8082"
    echo ""
    echo "🛑 To stop all services, run:"
    echo "   pkill -f 'python3.*service\.py'"
else
    echo "❌ Some services failed to start. Check the logs above."
    exit 1
fi
