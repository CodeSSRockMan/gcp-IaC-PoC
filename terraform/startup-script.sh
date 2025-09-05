#!/bin/bash
# Enhanced startup script for Medical Appointments Instance
set -e

# Log all activities
exec 1> >(tee -a /var/log/startup-script.log)
exec 2>&1

echo "🚀 Starting Medical Appointments Instance Setup..."

# Update system
apt-get update
apt-get install -y docker.io docker-compose nginx python3 python3-pip git curl wget unzip

# Start Docker
systemctl start docker
systemctl enable docker

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install and configure monitoring agents
curl -sSO https://dl.google.com/cloudagents/add-logging-agent-repo.sh
sudo bash add-logging-agent-repo.sh --also-install

curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh
sudo bash add-monitoring-agent-repo.sh --also-install

# Enable the monitoring and logging agents
systemctl enable google-cloud-ops-agent
systemctl start google-cloud-ops-agent

# Create app directory
mkdir -p /opt/medical-appointments
chown ubuntu:ubuntu /opt/medical-appointments

# Clone and setup the medical appointments app
cd /opt/medical-appointments

# Create the app files directly (since they're small)
cat > app.py << 'EOF'
#!/usr/bin/env python3
"""
Medical Appointments API - Firebase/Firestore Only
Self-contained medical appointments API with interactive health checks
"""
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

try:
    from google.cloud import firestore
    firebase_available = True
except ImportError:
    firebase_available = False

app = Flask(__name__)
CORS(app)

# Initialize Firebase if available
if firebase_available:
    try:
        db = firestore.Client()
        print("✅ Firebase connected")
    except:
        db = None
        firebase_available = False
        print("❌ Firebase not available")

APP_CONFIG = {
    'app_name': 'Medical Appointments API',
    'version': '3.0.0',
    'deployed_at': datetime.now().isoformat(),
    'backend': 'Firebase/Firestore'
}

@app.route('/')
@app.route('/medical-appointments/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏥 Medical Appointments API</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            .status {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .endpoint {{ background: #007bff; color: white; padding: 10px; margin: 5px 0; border-radius: 5px; }}
            .endpoint a {{ color: white; text-decoration: none; }}
            .healthy {{ color: green; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 {APP_CONFIG['app_name']}</h1>
            <p><strong>Version:</strong> {APP_CONFIG['version']}</p>
            <p><strong>Backend:</strong> Firebase/Firestore</p>
            <p><strong>Deployed:</strong> {APP_CONFIG['deployed_at']}</p>
            
            <div class="status">
                <h3>📊 System Status</h3>
                <p>Firebase: <span class="{'healthy' if firebase_available else 'error'}">
                   {'✅ Connected' if firebase_available else '❌ Not Available'}</span></p>
                <p>API Server: <span class="healthy">✅ Running</span></p>
            </div>
            
            <h3>🔗 Available Endpoints</h3>
            <div class="endpoint"><a href="/api/health">/api/health</a> - Health check</div>
            <div class="endpoint"><a href="/api/appointments">/api/appointments</a> - Appointments CRUD</div>
            <div class="endpoint"><a href="/api/patients">/api/patients</a> - Patients CRUD</div>
            <div class="endpoint"><a href="/api/doctors">/api/doctors</a> - Doctors CRUD</div>
            <div class="endpoint"><a href="/api/lang">/api/lang</a> - Language settings</div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': APP_CONFIG['version'],
        'firebase_connected': firebase_available
    })

@app.route('/api/appointments', methods=['GET', 'POST'])
def appointments():
    if request.method == 'POST':
        data = request.get_json() or {}
        return jsonify({'success': True, 'data': data, 'message': 'Appointment created'})
    return jsonify({'success': True, 'data': [], 'message': 'No appointments yet'})

@app.route('/api/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'POST':
        data = request.get_json() or {}
        return jsonify({'success': True, 'data': data, 'message': 'Patient created'})
    return jsonify({'success': True, 'data': [], 'message': 'No patients yet'})

@app.route('/api/doctors', methods=['GET', 'POST'])
def doctors():
    if request.method == 'POST':
        data = request.get_json() or {}
        return jsonify({'success': True, 'data': data, 'message': 'Doctor created'})
    return jsonify({'success': True, 'data': [], 'message': 'No doctors yet'})

@app.route('/api/lang')
def language():
    return jsonify({
        'supported_languages': ['en', 'es', 'fr'],
        'current_language': 'en',
        'status': 'working'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🏥 Medical Appointments API starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
flask==2.3.3
google-cloud-firestore==2.11.1
requests==2.31.0
flask-cors==4.0.0
python-dotenv==1.0.0
werkzeug==2.3.7
EOF

# Install Python dependencies
pip3 install -r requirements.txt

# Create nginx configuration for reverse proxy
cat > /etc/nginx/sites-available/medical-appointments << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    # Main health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Redirect root to medical appointments
    location = / {
        return 301 /medical-appointments/;
    }

    # Medical appointments app (main app)
    location /medical-appointments/ {
        proxy_pass http://localhost:8080/medical-appointments/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Dashboard fallback (in case someone accesses root)
    location / {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
rm -f /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/medical-appointments /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
systemctl enable nginx

# Create systemd service for medical appointments app
cat > /etc/systemd/system/medical-appointments.service << 'EOF'
[Unit]
Description=Medical Appointments API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/medical-appointments
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10
Environment=PORT=8080
Environment=GOOGLE_CLOUD_PROJECT=PROJECT_ID_PLACEHOLDER

[Install]
WantedBy=multi-user.target
EOF

# Replace project ID placeholder
sed -i "s/PROJECT_ID_PLACEHOLDER/$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")/g" /etc/systemd/system/medical-appointments.service

# Enable and start the medical appointments service
systemctl daemon-reload
systemctl enable medical-appointments
systemctl start medical-appointments

# Create monitoring script
cat > /opt/medical-appointments/monitor.sh << 'EOF'
#!/bin/bash
# Enhanced monitoring script

while true; do
    # Get current timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Memory usage
    MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    
    # Disk usage
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    # Network stats
    NETWORK_IN=$(cat /proc/net/dev | grep eth0 | awk '{print $2}')
    NETWORK_OUT=$(cat /proc/net/dev | grep eth0 | awk '{print $10}')
    
    # Log metrics
    echo "[$TIMESTAMP] CPU: ${CPU_USAGE}%, MEM: ${MEM_USAGE}%, DISK: ${DISK_USAGE}%, NET_IN: ${NETWORK_IN}, NET_OUT: ${NETWORK_OUT}" >> /var/log/system-metrics.log
    
    # Send to Google Cloud Monitoring (if available)
    if command -v gcloud &> /dev/null; then
        gcloud logging write medical-appointments-metrics "{\"timestamp\":\"$TIMESTAMP\",\"cpu\":\"$CPU_USAGE\",\"memory\":\"$MEM_USAGE\",\"disk\":\"$DISK_USAGE\"}" --severity=INFO 2>/dev/null || true
    fi
    
    sleep 60
done
EOF

chmod +x /opt/medical-appointments/monitor.sh

# Start monitoring in the background
nohup /opt/medical-appointments/monitor.sh > /dev/null 2>&1 &

# Wait for services to start
sleep 30

# Test that everything is working
echo "🧪 Testing services..."

# Test nginx
if curl -s http://localhost/health > /dev/null; then
    echo "✅ Nginx health check: OK"
else
    echo "❌ Nginx health check: FAIL"
fi

# Test medical appointments app
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Medical appointments app: OK"
else
    echo "❌ Medical appointments app: FAIL"
fi

# Test API endpoints
if curl -s http://localhost:8080/api/health > /dev/null; then
    echo "✅ API health check: OK"
else
    echo "❌ API health check: FAIL"
fi

# Show final status
echo "🎉 Medical Appointments Instance Setup Complete!"
echo "📊 Services Status:"
systemctl is-active --quiet nginx && echo "✅ Nginx: Running" || echo "❌ Nginx: Failed"
systemctl is-active --quiet medical-appointments && echo "✅ Medical Appointments API: Running" || echo "❌ Medical Appointments API: Failed"

echo "🔗 Access URLs:"
echo "   Main App: http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")/medical-appointments/"
echo "   API Health: http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")/api/health"

echo "📝 Logs available at:"
echo "   Startup: /var/log/startup-script.log"
echo "   App: journalctl -u medical-appointments -f"
echo "   Metrics: /var/log/system-metrics.log"

date >> /var/log/startup-script.log
echo "Startup script completed successfully" >> /var/log/startup-script.log
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Medical appointments API
    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Medical appointments app
    location /medical-appointments/ {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
rm -f /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/medical-appointments /etc/nginx/sites-enabled/
systemctl restart nginx
systemctl enable nginx

# Create systemd service for medical appointments app
cat > /etc/systemd/system/medical-appointments.service << 'EOF'
[Unit]
Description=Medical Appointments API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/medical-appointments
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10
Environment=PORT=8080
Environment=GOOGLE_CLOUD_PROJECT=PROJECT_ID_PLACEHOLDER

[Install]
WantedBy=multi-user.target
EOF

# Create dashboard service
cat > /etc/systemd/system/dashboard.service << 'EOF'
[Unit]
Description=Medical Appointments Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/medical-appointments
ExecStart=/usr/bin/python3 dashboard.py
Restart=always
RestartSec=10
Environment=PORT=5000
Environment=GOOGLE_CLOUD_PROJECT=PROJECT_ID_PLACEHOLDER

[Install]
WantedBy=multi-user.target
EOF

# Create monitoring script
cat > /opt/medical-appointments/monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script

while true; do
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Memory usage
    MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    
    # Disk usage
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    # Network
    NETWORK_IN=$(cat /proc/net/dev | grep eth0 | awk '{print $2}')
    NETWORK_OUT=$(cat /proc/net/dev | grep eth0 | awk '{print $10}')
    
    echo "$(date): CPU: ${CPU_USAGE}%, MEM: ${MEM_USAGE}%, DISK: ${DISK_USAGE}%, NET_IN: ${NETWORK_IN}, NET_OUT: ${NETWORK_OUT}" >> /var/log/system-metrics.log
    
    sleep 60
done
EOF

chmod +x /opt/medical-appointments/monitor.sh

# Create a simple health check web page
cat > /opt/medical-appointments/health.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Medical Appointments - Health Status</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .healthy { color: green; }
        .unhealthy { color: red; }
        .metric { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🏥 Medical Appointments Health Dashboard</h1>
    <div id="metrics">
        <div class="metric">
            <strong>Instance Status:</strong> 
            <span class="healthy">● Running</span>
        </div>
        <div class="metric">
            <strong>Last Updated:</strong> <span id="timestamp"></span>
        </div>
    </div>
    
    <script>
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
EOF

echo "Startup script completed successfully" >> /var/log/startup-script.log
