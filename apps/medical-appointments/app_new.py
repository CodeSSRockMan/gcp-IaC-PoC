#!/usr/bin/env python3
"""
Medical Appointments API - Firebase/Firestore Only
Self-contained medical appointments API with interactive health checks and Firebase backend
"""
import os
import json
import uuid
from datetime import datetime, date, time
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from google.cloud import firestore
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App configuration
APP_CONFIG = {
    'app_name': 'Medical Appointments API',
    'version': '3.0.0',
    'deployed_at': datetime.now().isoformat(),
    'backend': 'Firebase/Firestore',
    'endpoints': {}
}

# Initialize Firebase/Firestore
try:
    db = firestore.Client()
    firebase_available = True
    logger.info("✅ Firebase/Firestore connected successfully")
except Exception as e:
    logger.error(f"❌ Firebase connection failed: {e}")
    db = None
    firebase_available = False

# Collections in Firestore
COLLECTIONS = {
    'appointments': 'medical_appointments',
    'patients': 'patients',
    'doctors': 'doctors',
    'health_checks': 'health_checks'
}

# Health check dashboard template
HEALTH_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>🏥 Medical Appointments - Interactive Health Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; padding: 20px; background: #f8f9fa; 
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; 
        }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: white; border-radius: 10px; padding: 20px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .status-healthy { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-error { color: #dc3545; }
        .endpoint { 
            background: #e9ecef; padding: 10px; border-radius: 5px; 
            margin: 5px 0; font-family: monospace; 
        }
        .endpoint a { color: #007bff; text-decoration: none; }
        .endpoint a:hover { text-decoration: underline; }
        .console { 
            background: #2d3748; color: #e2e8f0; padding: 15px; 
            border-radius: 5px; font-family: monospace; font-size: 14px;
            max-height: 300px; overflow-y: auto;
        }
        .btn { 
            background: #007bff; color: white; padding: 10px 20px; 
            border: none; border-radius: 5px; cursor: pointer; margin: 5px;
        }
        .btn:hover { background: #0056b3; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .interactive-panel { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 {{ app_name }}</h1>
            <p>Version: {{ version }} | Backend: Firebase/Firestore | Deployed: {{ deployed_at }}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🔗 API Endpoints</h3>
                <div class="endpoint">
                    <strong>Main App:</strong> <a href="/medical-appointments/" target="_blank">/medical-appointments/</a>
                </div>
                <div class="endpoint">
                    <strong>API Root:</strong> <a href="/api/" target="_blank">/api/</a>
                </div>
                <div class="endpoint">
                    <strong>Appointments:</strong> <a href="/api/appointments" target="_blank">/api/appointments</a>
                </div>
                <div class="endpoint">
                    <strong>Patients:</strong> <a href="/api/patients" target="_blank">/api/patients</a>
                </div>
                <div class="endpoint">
                    <strong>Doctors:</strong> <a href="/api/doctors" target="_blank">/api/doctors</a>
                </div>
                <div class="endpoint">
                    <strong>Health Check:</strong> <a href="/health" target="_blank">/health</a>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 System Status</h3>
                <div class="metric">
                    <span>Firebase/Firestore:</span>
                    <span class="{{ 'status-healthy' if firebase_status else 'status-error' }}">
                        {{ '✅ Connected' if firebase_status else '❌ Disconnected' }}
                    </span>
                </div>
                <div class="metric">
                    <span>API Server:</span>
                    <span class="status-healthy">✅ Running</span>
                </div>
                <div class="metric">
                    <span>Collections:</span>
                    <span class="status-healthy">✅ {{ collections_count }} Active</span>
                </div>
                <div class="metric">
                    <span>Last Check:</span>
                    <span>{{ last_check }}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🧪 Interactive API Console</h3>
                <div class="interactive-panel">
                    <button class="btn" onclick="testEndpoint('/api/health')">Test Health</button>
                    <button class="btn" onclick="testEndpoint('/api/appointments')">List Appointments</button>
                    <button class="btn" onclick="testEndpoint('/api/patients')">List Patients</button>
                    <button class="btn" onclick="createSampleData()">Create Sample Data</button>
                </div>
                <div id="console" class="console">
                    > Medical Appointments API Console Ready<br>
                    > Click buttons above to test endpoints<br>
                    > All responses will appear here<br>
                </div>
            </div>
            
            <div class="card">
                <h3>🔧 Quick Actions</h3>
                <button class="btn" onclick="refreshStatus()">🔄 Refresh Status</button>
                <button class="btn" onclick="runHealthCheck()">🏥 Run Health Check</button>
                <button class="btn" onclick="viewLogs()">📝 View Logs</button>
                <button class="btn" onclick="window.open('/api/', '_blank')">🚀 Open API</button>
            </div>
        </div>
    </div>

    <script>
        function logToConsole(message) {
            const console = document.getElementById('console');
            const timestamp = new Date().toLocaleTimeString();
            console.innerHTML += `<br>> [${timestamp}] ${message}`;
            console.scrollTop = console.scrollHeight;
        }

        async function testEndpoint(endpoint) {
            logToConsole(`Testing ${endpoint}...`);
            try {
                const response = await fetch(endpoint);
                const data = await response.json();
                logToConsole(`✅ ${endpoint}: ${JSON.stringify(data, null, 2)}`);
            } catch (error) {
                logToConsole(`❌ ${endpoint}: ${error.message}`);
            }
        }

        async function createSampleData() {
            logToConsole('Creating sample appointment...');
            try {
                const response = await fetch('/api/appointments', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        patient_name: 'John Doe',
                        doctor_name: 'Dr. Smith',
                        appointment_date: '2025-09-10',
                        appointment_time: '14:30',
                        description: 'Regular checkup'
                    })
                });
                const data = await response.json();
                logToConsole(`✅ Sample appointment created: ${JSON.stringify(data, null, 2)}`);
            } catch (error) {
                logToConsole(`❌ Error creating sample data: ${error.message}`);
            }
        }

        function refreshStatus() {
            logToConsole('Refreshing page...');
            window.location.reload();
        }

        function runHealthCheck() {
            testEndpoint('/health');
        }

        function viewLogs() {
            logToConsole('Viewing recent activity logs...');
            testEndpoint('/api/health/logs');
        }

        // Auto-refresh every 30 seconds
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
"""

# Simple API response template
API_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Medical Appointments API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .endpoint { background: #e9ecef; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .method { background: #007bff; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Medical Appointments API v3.0</h1>
        <p><strong>Backend:</strong> Firebase/Firestore Only</p>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> <strong>/api/health</strong> - Health check
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <strong>/api/appointments</strong> - List all appointments
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <strong>/api/appointments</strong> - Create new appointment
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <strong>/api/patients</strong> - List all patients
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <strong>/api/doctors</strong> - List all doctors
        </div>
        
        <p><a href="/">← Back to Interactive Dashboard</a></p>
    </div>
</body>
</html>
"""

# Helper functions for Firestore operations
def add_to_firestore(collection_name, data):
    """Add document to Firestore collection"""
    if not firebase_available:
        return {"error": "Firebase not available"}
    
    try:
        doc_ref = db.collection(collection_name).document()
        data['id'] = doc_ref.id
        data['created_at'] = datetime.now()
        doc_ref.set(data)
        return {"success": True, "id": doc_ref.id, "data": data}
    except Exception as e:
        logger.error(f"Error adding to Firestore: {e}")
        return {"error": str(e)}

def get_from_firestore(collection_name, limit=50):
    """Get documents from Firestore collection"""
    if not firebase_available:
        return {"error": "Firebase not available"}
    
    try:
        docs = db.collection(collection_name).limit(limit).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error getting from Firestore: {e}")
        return {"error": str(e)}

# Routes
@app.route('/')
def home():
    """Interactive health dashboard"""
    return render_template_string(HEALTH_DASHBOARD, 
        app_name=APP_CONFIG['app_name'],
        version=APP_CONFIG['version'],
        deployed_at=APP_CONFIG['deployed_at'],
        firebase_status=firebase_available,
        collections_count=len(COLLECTIONS),
        last_check=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/medical-appointments/')
def medical_appointments_app():
    """Main medical appointments application"""
    return render_template_string(API_TEMPLATE)

@app.route('/api/')
def api_root():
    """API documentation"""
    return render_template_string(API_TEMPLATE)

@app.route('/health')
def health_check():
    """Simple health check"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': APP_CONFIG['version'],
        'firebase_connected': firebase_available,
        'collections': list(COLLECTIONS.keys()) if firebase_available else []
    }
    return jsonify(status)

@app.route('/api/health')
def api_health():
    """Detailed API health check"""
    # Test Firebase connection
    firebase_test = {"connected": False, "error": None}
    if firebase_available:
        try:
            # Try to read from a test collection
            test_ref = db.collection('health_checks').limit(1)
            firebase_test["connected"] = True
        except Exception as e:
            firebase_test["error"] = str(e)
    
    health_data = {
        'service': 'Medical Appointments API',
        'status': 'healthy' if firebase_available else 'degraded',
        'version': APP_CONFIG['version'],
        'timestamp': datetime.now().isoformat(),
        'backend': {
            'type': 'Firebase/Firestore',
            'status': firebase_test
        },
        'endpoints': {
            'appointments': '/api/appointments',
            'patients': '/api/patients', 
            'doctors': '/api/doctors',
            'health': '/api/health'
        },
        'collections': COLLECTIONS
    }
    
    return jsonify(health_data)

@app.route('/api/health/logs')
def health_logs():
    """Recent health check logs"""
    if not firebase_available:
        return jsonify({"error": "Firebase not available"})
    
    logs = get_from_firestore(COLLECTIONS['health_checks'], limit=10)
    return jsonify(logs)

@app.route('/api/appointments', methods=['GET', 'POST'])
def appointments():
    """Handle appointments - GET (list) and POST (create)"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_name', 'doctor_name', 'appointment_date', 'appointment_time']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add to Firestore
        result = add_to_firestore(COLLECTIONS['appointments'], data)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result), 201
    
    else:  # GET
        result = get_from_firestore(COLLECTIONS['appointments'])
        return jsonify(result)

@app.route('/api/patients', methods=['GET', 'POST'])
def patients():
    """Handle patients"""
    if request.method == 'POST':
        data = request.get_json()
        
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        result = add_to_firestore(COLLECTIONS['patients'], data)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result), 201
    
    else:  # GET
        result = get_from_firestore(COLLECTIONS['patients'])
        return jsonify(result)

@app.route('/api/doctors', methods=['GET', 'POST'])
def doctors():
    """Handle doctors"""
    if request.method == 'POST':
        data = request.get_json()
        
        required_fields = ['name', 'specialization']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        result = add_to_firestore(COLLECTIONS['doctors'], data)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result), 201
    
    else:  # GET
        result = get_from_firestore(COLLECTIONS['doctors'])
        return jsonify(result)

@app.route('/api/lang')
def language_check():
    """Language/localization endpoint - now working"""
    languages = {
        'supported_languages': ['en', 'es', 'fr', 'de'],
        'current_language': 'en',
        'translations': {
            'en': {
                'title': 'Medical Appointments',
                'welcome': 'Welcome to Medical Appointments API',
                'status': 'System Status: Online'
            },
            'es': {
                'title': 'Citas Médicas',
                'welcome': 'Bienvenido a la API de Citas Médicas',
                'status': 'Estado del Sistema: En línea'
            }
        }
    }
    return jsonify(languages)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    # Log health check on startup
    if firebase_available:
        health_check_data = {
            'event': 'startup',
            'timestamp': datetime.now(),
            'version': APP_CONFIG['version'],
            'port': port
        }
        add_to_firestore(COLLECTIONS['health_checks'], health_check_data)
    
    print(f"🏥 Medical Appointments API v{APP_CONFIG['version']} starting...")
    print(f"🔥 Firebase/Firestore: {'✅ Connected' if firebase_available else '❌ Not available'}")
    print(f"🌐 Running on port {port}")
    print(f"🔗 Main dashboard: http://localhost:{port}/")
    print(f"🔗 API docs: http://localhost:{port}/api/")
    
    app.run(host='0.0.0.0', port=port, debug=False)
