#!/usr/bin/env python3
"""
Compute Service - Main Python Application Server
Serves your Python application with GCP integration
"""
import os
import json
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from google.cloud import firestore, storage

app = Flask(__name__)

# Initialize GCP clients
try:
    db = firestore.Client()
    storage_client = storage.Client()
    gcp_available = True
except Exception as e:
    print(f"GCP services not available: {e}")
    db = None
    storage_client = None
    gcp_available = False

# App configuration
APP_CONFIG = {
    'deployed_at': datetime.now().isoformat(),
    'auto_scale': True,
    'storage_bucket': None,
    'database': None,
    'status': 'running',
    'external_apps': {}  # Store multiple external app configurations
}

# Sample data store
DATA_STORE = []

# Multiple app configurations
REGISTERED_APPS = {
    'my-app': {
        'name': 'My Custom App',
        'description': 'My custom Python application',
        'route': '/my-app',
        'enabled': True
    },
    'medical-appointments': {
        'name': 'Medical Appointments API',
        'description': 'Full-featured medical appointment scheduling system',
        'route': '/medical-appointments',
        'enabled': True
    },
    'data-analytics': {
        'name': 'Data Analytics',
        'description': 'Data processing and visualization',
        'route': '/analytics',
        'enabled': False
    },
    'api-service': {
        'name': 'API Service',
        'description': 'REST API endpoints',
        'route': '/api-v2',
        'enabled': False
    }
}

def validate_api_request():
    """Simple validation for API requests"""
    return True  # Simplified for now

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok', 
        'service': 'compute', 
        'app_ready': True,
        'gcp_available': gcp_available,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/deploy', methods=['POST'])
def deploy_app():
    """Deploy Python app configuration"""
    config = request.json or {}
    APP_CONFIG.update({
        'auto_scale': config.get('auto_scale', True),
        'storage_bucket': config.get('storage_bucket'),
        'database': config.get('database'),
        'deployed_at': datetime.now().isoformat()
    })
    
    app.logger.info(f"App deployed with config: {APP_CONFIG}")
    return jsonify({'status': 'deployed', 'config': APP_CONFIG})

@app.route('/configure', methods=['POST'])
def configure():
    """Configure compute service"""
    config = request.json or {}
    app.logger.info(f"Service configured: {config}")
    return jsonify({'status': 'configured'})

# ===== MAIN PYTHON APPLICATION ROUTES =====

@app.route('/')
def main_app():
    """Main Python application interface"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Python App on GCP</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { 
                max-width: 1000px; margin: 0 auto; 
                background: white; padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header { 
                color: #4285f4; 
                border-bottom: 3px solid #4285f4; 
                padding-bottom: 15px; 
                margin-bottom: 30px;
                text-align: center;
            }
            .feature-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                gap: 20px; 
                margin: 30px 0;
            }
            .feature { 
                padding: 20px; 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                border-radius: 10px; 
                border-left: 5px solid #4285f4;
                transition: transform 0.3s ease;
            }
            .feature:hover { 
                transform: translateY(-5px); 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .btn { 
                display: inline-block; 
                padding: 12px 24px; 
                background: #4285f4; 
                color: white; 
                text-decoration: none; 
                border-radius: 25px; 
                margin: 8px 5px; 
                font-weight: 500;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
            }
            .btn:hover { 
                background: #3367d6; 
                transform: translateY(-2px);
            }
            .btn-success { background: #34a853; }
            .btn-warning { background: #fbbc04; color: #333; }
            .status { 
                display: inline-block;
                padding: 5px 10px; 
                border-radius: 15px; 
                font-size: 0.9em; 
                font-weight: bold;
            }
            .status.online { background: #d4edda; color: #155724; }
            .status.offline { background: #f8d7da; color: #721c24; }
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .info-item {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #28a745;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Python App on GCP</h1>
                <p>OpenStack-equivalent Serverless Infrastructure</p>
                <span class="status {{ 'online' if gcp_available else 'offline' }}">
                    {{ '● GCP Connected' if gcp_available else '● Local Mode' }}
                </span>
            </div>
            
            <div class="feature-grid">
                <div class="feature">
                    <h3>📊 Data Management</h3>
                    <p>Manage your application data with Firestore integration</p>
                    <a href="/data" class="btn btn-success">View Data</a>
                    <a href="/data/add" class="btn">Add Data</a>
                </div>
                
                <div class="feature">
                    <h3>☁️ File Storage</h3>
                    <p>Upload and manage files in Google Cloud Storage</p>
                    <a href="/upload" class="btn btn-warning">Upload File</a>
                    <a href="/files" class="btn">Browse Files</a>
                </div>
                
                <div class="feature">
                    <h3>🔧 System Tools</h3>
                    <p>System information and administrative tools</p>
                    <a href="/shell" class="btn">Shell Access</a>
                    <a href="/stats" class="btn">Statistics</a>
                </div>
                
                <div class="feature">
                    <h3>🌐 API Access</h3>
                    <p>REST API endpoints for programmatic access</p>
                    <a href="/api/status" class="btn">API Status</a>
                    <a href="/api/docs" class="btn">Documentation</a>
                </div>
                
                <div class="feature">
                    <h3>🚀 Python Apps</h3>
                    <p>Manage and access your Python applications</p>
                    <a href="/apps" class="btn btn-primary">View Apps</a>
                    <a href="/my-app" class="btn">My Custom App</a>
                </div>
                
                <div class="feature">
                    <h3>🔗 External Apps</h3>
                    <p>Link to external Python applications</p>
                    <a href="/external-app" class="btn">Access External</a>
                    <a href="/load-app-form" class="btn btn-success">Configure</a>
                </div>
            </div>
            
            <div class="feature">
                <h3>📋 System Information</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Deployed:</strong><br>{{ deployed_time }}
                    </div>
                    <div class="info-item">
                        <strong>Auto-scaling:</strong><br>{{ auto_scale_status }}
                    </div>
                    <div class="info-item">
                        <strong>Storage:</strong><br>{{ storage_status }}
                    </div>
                    <div class="info-item">
                        <strong>Database:</strong><br>{{ database_status }}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """, 
    deployed_time=APP_CONFIG['deployed_at'][:19].replace('T', ' '),
    auto_scale_status='Enabled' if APP_CONFIG['auto_scale'] else 'Disabled',
    storage_status='Connected' if APP_CONFIG['storage_bucket'] else 'Not configured',
    database_status='Connected' if APP_CONFIG['database'] else 'Not configured',
    gcp_available=gcp_available
    )

@app.route('/data')
def view_data():
    """View stored data"""
    try:
        if gcp_available and db and APP_CONFIG['database']:
            # Fetch from Firestore
            docs = db.collection('app_data').limit(10).stream()
            firestore_data = [{'id': doc.id, **doc.to_dict()} for doc in docs]
        else:
            firestore_data = []
        
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Management</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .header { color: #4285f4; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
                .data-item { background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; }
                .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
                .empty { text-align: center; color: #666; padding: 40px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">Data Management</h1>
                <a href="/" class="btn">← Back to App</a>
                <a href="/data/add" class="btn">Add New Data</a>
                
                {% if firestore_data %}
                    <h3>Firestore Data:</h3>
                    {% for item in firestore_data %}
                    <div class="data-item">
                        <strong>ID:</strong> {{ item.id }}<br>
                        {% for key, value in item.items() %}
                            {% if key != 'id' %}
                                <strong>{{ key }}:</strong> {{ value }}<br>
                            {% endif %}
                        {% endfor %}
                    </div>
                    {% endfor %}
                {% endif %}
                
                {% if local_data %}
                    <h3>Local Data:</h3>
                    {% for item in local_data %}
                    <div class="data-item">
                        <strong>Entry {{ loop.index }}:</strong> {{ item }}
                    </div>
                    {% endfor %}
                {% endif %}
                
                {% if not firestore_data and not local_data %}
                    <div class="empty">
                        <h3>No data found</h3>
                        <p>Add some data to get started!</p>
                    </div>
                {% endif %}
            </div>
        </body>
        </html>
        """, firestore_data=firestore_data, local_data=DATA_STORE)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data/add', methods=['GET', 'POST'])
def add_data():
    """Add new data"""
    if request.method == 'POST':
        try:
            data = {
                'content': request.form.get('content', ''),
                'timestamp': datetime.now().isoformat(),
                'type': request.form.get('type', 'text')
            }
            
            if gcp_available and db and APP_CONFIG['database']:
                # Store in Firestore
                db.collection('app_data').add(data)
                message = "Data stored in Firestore successfully!"
            else:
                # Store locally
                DATA_STORE.append(data)
                message = "Data stored locally successfully!"
            
            return redirect(url_for('view_data'))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Data</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .header { color: #4285f4; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 5px; border: none; cursor: pointer; }
            .btn:hover { background: #3367d6; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">Add New Data</h1>
            <a href="/data" class="btn">← Back to Data</a>
            
            <form method="POST">
                <div class="form-group">
                    <label for="type">Data Type:</label>
                    <select name="type" id="type">
                        <option value="text">Text</option>
                        <option value="note">Note</option>
                        <option value="config">Configuration</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="content">Content:</label>
                    <textarea name="content" id="content" rows="5" required placeholder="Enter your data here..."></textarea>
                </div>
                <button type="submit" class="btn">Save Data</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """File upload interface"""
    if request.method == 'POST':
        return jsonify({
            'message': 'File upload functionality would be implemented here',
            'gcp_available': gcp_available,
            'bucket': APP_CONFIG['storage_bucket']
        })
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>File Upload</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .header { color: #4285f4; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
            .upload-area { border: 2px dashed #ddd; padding: 40px; text-align: center; margin: 20px 0; border-radius: 8px; }
            .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">File Upload</h1>
            <a href="/" class="btn">← Back to App</a>
            
            <div class="upload-area">
                <h3>Upload Files to GCP Storage</h3>
                <p>Storage Status: {{ 'Available' if gcp_available else 'Not Available' }}</p>
                <p>Bucket: {{ bucket or 'Not configured' }}</p>
                <form method="POST" enctype="multipart/form-data">
                    <input type="file" name="file" multiple>
                    <br><br>
                    <button type="submit" class="btn">Upload</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """, gcp_available=gcp_available, bucket=APP_CONFIG['storage_bucket'])

@app.route('/shell')
def shell_access():
    """Simple shell interface"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shell Access</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .header { color: #4285f4; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
            .terminal { background: #000; color: #0f0; padding: 20px; border-radius: 5px; font-family: monospace; margin: 20px 0; }
            .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
            .command-list { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">Shell Access</h1>
            <a href="/" class="btn">← Back to App</a>
            
            <div class="terminal">
                <div>user@python-app:~$ Welcome to the Python App Shell</div>
                <div>user@python-app:~$ Available commands: /shell/execute</div>
                <div>user@python-app:~$ Type commands below (limited for security)</div>
            </div>
            
            <div class="command-list">
                <h3>Available Commands:</h3>
                <ul>
                    <li><a href="/shell/execute?cmd=ls">ls</a> - List files</li>
                    <li><a href="/shell/execute?cmd=pwd">pwd</a> - Current directory</li>
                    <li><a href="/shell/execute?cmd=whoami">whoami</a> - Current user</li>
                    <li><a href="/shell/execute?cmd=date">date</a> - Current date/time</li>
                    <li><a href="/shell/execute?cmd=ps">ps</a> - Running processes</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route('/shell/execute')
def execute_command():
    """Execute safe shell commands"""
    cmd = request.args.get('cmd', '')
    allowed_commands = {
        'ls': ['ls', '-la'],
        'pwd': ['pwd'],
        'whoami': ['whoami'],
        'date': ['date'],
        'ps': ['ps', 'aux']
    }
    
    if cmd in allowed_commands:
        try:
            result = subprocess.run(allowed_commands[cmd], capture_output=True, text=True, timeout=5)
            output = result.stdout + result.stderr
        except Exception as e:
            output = f"Error: {str(e)}"
    else:
        output = f"Command '{cmd}' not allowed or not found"
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Command Output</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .header { color: #4285f4; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
            .output { background: #000; color: #0f0; padding: 20px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }
            .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">Command Output: {{ cmd }}</h1>
            <a href="/shell" class="btn">← Back to Shell</a>
            
            <div class="output">{{ output }}</div>
        </div>
    </body>
    </html>
    """, cmd=cmd, output=output)

@app.route('/stats')
def statistics():
    """Show app statistics"""
    stats = {
        'uptime': (datetime.now() - datetime.fromisoformat(APP_CONFIG['deployed_at'])).total_seconds(),
        'data_count': len(DATA_STORE),
        'gcp_status': 'Connected' if gcp_available else 'Offline',
        'auto_scale': APP_CONFIG['auto_scale'],
        'storage_bucket': APP_CONFIG['storage_bucket'] or 'Not configured',
        'database': APP_CONFIG['database'] or 'Not configured'
    }
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Statistics</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .header { color: #4285f4; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
            .stat-item { background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 5px; display: flex; justify-content: space-between; }
            .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">Application Statistics</h1>
            <a href="/" class="btn">← Back to App</a>
            
            <div class="stat-item">
                <strong>Uptime:</strong>
                <span>{{ "%.2f"|format(stats.uptime) }} seconds</span>
            </div>
            <div class="stat-item">
                <strong>Data Entries:</strong>
                <span>{{ stats.data_count }}</span>
            </div>
            <div class="stat-item">
                <strong>GCP Status:</strong>
                <span>{{ stats.gcp_status }}</span>
            </div>
            <div class="stat-item">
                <strong>Auto-scaling:</strong>
                <span>{{ 'Enabled' if stats.auto_scale else 'Disabled' }}</span>
            </div>
            <div class="stat-item">
                <strong>Storage Bucket:</strong>
                <span>{{ stats.storage_bucket }}</span>
            </div>
            <div class="stat-item">
                <strong>Database:</strong>
                <span>{{ stats.database }}</span>
            </div>
        </div>
    </body>
    </html>
    """, stats=stats)

# ===== API ROUTES =====

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'service': 'compute',
        'status': 'running',
        'version': '1.0.0',
        'gcp_available': gcp_available,
        'timestamp': datetime.now().isoformat(),
        'config': APP_CONFIG
    })

@app.route('/api/docs')
def api_docs():
    """API documentation"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .header { color: #4285f4; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
            .endpoint { background: #f8f9fa; margin: 15px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; }
            .method { background: #007bff; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; }
            .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">API Documentation</h1>
            <a href="/" class="btn">← Back to App</a>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p>Health check endpoint</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /api/status</h3>
                <p>Detailed service status and configuration</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /deploy</h3>
                <p>Deploy application configuration</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /configure</h3>
                <p>Configure service settings</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /data</h3>
                <p>View application data</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /data/add</h3>
                <p>Add new data entry</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route('/load-app', methods=['POST'])
def load_external_app():
    """Load external Python application from URL"""
    config = request.json or {}
    app_url = config.get('app_url')
    app_type = config.get('type', 'proxy')  # 'proxy' or 'download'
    
    if not app_url:
        return jsonify({'error': 'app_url required'}), 400
    
    if app_type == 'proxy':
        # Store the URL for proxying requests
        APP_CONFIG['external_app_url'] = app_url
        app.logger.info(f"Configured to proxy to external app: {app_url}")
        return jsonify({
            'status': 'configured',
            'type': 'proxy',
            'app_url': app_url,
            'message': 'Requests to /external-app/* will be proxied to your app'
        })
    
    return jsonify({'error': 'Unsupported app type'}), 400

@app.route('/external-app')
@app.route('/external-app/<path:path>')
def proxy_external_app(path=''):
    """Proxy requests to external Python application"""
    external_url = APP_CONFIG.get('external_app_url')
    
    if not external_url:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>External App Not Configured</title></head>
        <body style="font-family: Arial; margin: 40px; text-align: center;">
            <h1>🔗 External App Loader</h1>
            <p>No external application URL configured.</p>
            <p>Use the <code>/load-app</code> endpoint to configure an external Python app.</p>
            <a href="/" style="color: #4285f4;">← Back to Main App</a>
        </body>
        </html>
        """)
    
    try:
        import requests
        target_url = f"{external_url.rstrip('/')}/{path}"
        
        # Proxy the request
        if request.method == 'GET':
            resp = requests.get(target_url, params=request.args, timeout=30)
        else:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers={key: value for (key, value) in request.headers if key != 'Host'},
                data=request.get_data(),
                params=request.args,
                timeout=30
            )
        
        return resp.content, resp.status_code, resp.headers.items()
        
    except Exception as e:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>External App Error</title></head>
        <body style="font-family: Arial; margin: 40px; text-align: center;">
            <h1>⚠️ External App Unavailable</h1>
            <p>Could not connect to external application: {{ error }}</p>
            <p><strong>App URL:</strong> {{ app_url }}</p>
            <a href="/" style="color: #4285f4;">← Back to Main App</a>
        </body>
        </html>
        """, error=str(e), app_url=external_url), 503

@app.route('/apps')
def list_apps():
    """List all available Python applications"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Available Python Apps</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .app-card { border: 1px solid #ddd; padding: 20px; margin: 15px 0; border-radius: 8px; background: #f9f9f9; }
            .app-card.enabled { border-left: 4px solid #28a745; }
            .app-card.disabled { border-left: 4px solid #dc3545; opacity: 0.7; }
            .btn { padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; }
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-secondary { background: #6c757d; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Available Python Applications</h1>
            <p>Choose from the applications available on this server:</p>
            
            {% for app_id, app in registered_apps.items() %}
            <div class="app-card {{ 'enabled' if app.enabled else 'disabled' }}">
                <h3>{{ app.name }}</h3>
                <p>{{ app.description }}</p>
                <p><strong>Route:</strong> <code>{{ app.route }}</code></p>
                
                {% if app.enabled %}
                    <a href="{{ app.route }}" class="btn btn-primary">Open App</a>
                    <span style="color: #28a745;">● Active</span>
                {% else %}
                    <button class="btn btn-secondary" disabled>Not Available</button>
                    <span style="color: #dc3545;">● Disabled</span>
                {% endif %}
            </div>
            {% endfor %}
            
            <div class="app-card enabled">
                <h3>External Apps</h3>
                <p>Link to external Python applications via proxy</p>
                <p><strong>Route:</strong> <code>/external-app</code></p>
                <a href="/external-app" class="btn btn-primary">Access External App</a>
                <a href="/load-app-form" class="btn btn-success">Configure External App</a>
            </div>
            
            <hr style="margin: 30px 0;">
            <a href="/" class="btn btn-secondary">← Back to Main App</a>
        </div>
    </body>
    </html>
    """, registered_apps=REGISTERED_APPS)

@app.route('/load-app-form')
def load_app_form():
    """Web form to configure external app"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Configure External App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
            .btn { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #0056b3; }
            .btn-secondary { background: #6c757d; text-decoration: none; display: inline-block; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔗 Configure External Python App</h1>
            <p>Link your external Python application to this infrastructure:</p>
            
            <form id="appForm">
                <div class="form-group">
                    <label for="app_url">Application URL:</label>
                    <input type="url" id="app_url" name="app_url" 
                           placeholder="https://your-python-app.com" required>
                </div>
                
                <div class="form-group">
                    <label for="type">Integration Type:</label>
                    <select id="type" name="type">
                        <option value="proxy">Proxy (Recommended)</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">Configure App</button>
                <a href="/apps" class="btn btn-secondary">Cancel</a>
            </form>
            
            <div id="result" style="margin-top: 20px; display: none;"></div>
        </div>
        
        <script>
            document.getElementById('appForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                try {
                    const response = await fetch('/load-app', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('result');
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 4px;">
                                <h3>✅ Success!</h3>
                                <p>${result.message}</p>
                                <p><strong>Your app is now available at:</strong> <a href="/external-app">/external-app</a></p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px;">
                                <h3>❌ Error</h3>
                                <p>${result.error}</p>
                            </div>
                        `;
                    }
                    
                    resultDiv.style.display = 'block';
                } catch (error) {
                    console.error('Error:', error);
                }
            });
        </script>
    </body>
    </html>
    """)

# Example custom app routes (you can add your own here)
@app.route('/my-app')
def my_custom_app():
    """Your custom Python application"""
    if not REGISTERED_APPS['my-app']['enabled']:
        return "This app is currently disabled", 404
        
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Custom App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .feature-box { background: #e3f2fd; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #2196f3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 My Custom Python App</h1>
            <p>This is where your custom Python application logic goes!</p>
            
            <div class="feature-box">
                <h3>🚀 Auto-scaling Features</h3>
                <p>Your app automatically scales with Cloud Run:</p>
                <ul>
                    <li>✅ Scales from 0 to unlimited instances</li>
                    <li>✅ Pay only for actual usage</li>
                    <li>✅ Automatic load balancing</li>
                    <li>✅ Built-in health monitoring</li>
                </ul>
            </div>
            
            <div class="feature-box">
                <h3>🔧 Available Resources</h3>
                <p>Your app has access to:</p>
                <ul>
                    <li>📊 Firestore Database: <code>{{ 'Connected' if gcp_available else 'Local Mode' }}</code></li>
                    <li>☁️ Cloud Storage: <code>{{ 'Available' if gcp_available else 'Local Mode' }}</code></li>
                    <li>🌐 REST API endpoints</li>
                    <li>🔒 Secure VPC networking</li>
                </ul>
            </div>
            
            <!-- Add your custom app content here -->
            <div class="feature-box">
                <h3>💡 Add Your Code Here</h3>
                <p>Replace this section with your actual Python application:</p>
                <pre style="background: #f4f4f4; padding: 15px; border-radius: 4px;">
# Example: Add your routes in compute-service.py
@app.route('/my-app/feature1')
def my_feature():
    # Your Python logic here
    return "Hello from your custom feature!"
                </pre>
            </div>
            
            <hr style="margin: 30px 0;">
            <a href="/apps" style="color: #007bff; text-decoration: none;">← Back to App List</a> |
            <a href="/" style="color: #007bff; text-decoration: none;">Main Dashboard</a>
        </div>
    </body>
    </html>
    """, gcp_available=gcp_available)

@app.route('/medical-appointments')
@app.route('/medical-appointments/<path:path>')
def medical_appointments_app(path=''):
    """Medical Appointments API - Full Featured System"""
    if not REGISTERED_APPS['medical-appointments']['enabled']:
        return "Medical Appointments API is currently disabled", 404
    
    try:
        # Import the medical appointments service
        import requests
        import subprocess
        import time
        from threading import Thread
        
        # Check if medical appointments service is running on port 8080
        try:
            response = requests.get('http://localhost:8080/health', timeout=2)
            if response.status_code == 200:
                # Service is running, proxy the request
                target_url = f"http://localhost:8080/{path}" if path else "http://localhost:8080/"
                
                if request.method == 'GET':
                    resp = requests.get(target_url, params=request.args, timeout=30)
                else:
                    resp = requests.request(
                        method=request.method,
                        url=target_url,
                        headers={key: value for (key, value) in request.headers if key != 'Host'},
                        data=request.get_data(),
                        params=request.args,
                        timeout=30
                    )
                
                return resp.content, resp.status_code, resp.headers.items()
        except requests.exceptions.RequestException:
            pass
        
        # Service not running, show information page
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Medical Appointments API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .feature-box { background: #e8f5e8; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #4caf50; }
                .info-box { background: #fff3cd; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ffc107; }
                .btn { display: inline-block; padding: 12px 24px; background: #4caf50; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
                .btn:hover { background: #45a049; }
                .command { background: #f4f4f4; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 Medical Appointments API</h1>
                <p>Full-featured medical appointment scheduling system integrated with your GCP infrastructure.</p>
                
                <div class="info-box">
                    <h3>📋 Service Status</h3>
                    <p><strong>Status:</strong> Not currently running</p>
                    <p><strong>Expected Port:</strong> 8080</p>
                    <p>To start the service, run the following command:</p>
                    <div class="command">cd /Users/pramosba/gcp-IaC-PoC/services && python medical-appointments-service.py</div>
                </div>
                
                <div class="feature-box">
                    <h3>🚀 Auto-scaling Features</h3>
                    <p>The Medical Appointments API includes:</p>
                    <ul>
                        <li>✅ Auto-scaling with Cloud Run</li>
                        <li>✅ SQLAlchemy with MySQL/SQLite fallback</li>
                        <li>✅ Firestore integration for backup</li>
                        <li>✅ RESTful API endpoints</li>
                        <li>✅ Multi-language support (English/Spanish)</li>
                        <li>✅ CORS enabled for web applications</li>
                        <li>✅ Comprehensive test suite</li>
                    </ul>
                </div>
                
                <div class="feature-box">
                    <h3>🔧 API Endpoints</h3>
                    <p>Available when service is running:</p>
                    <ul>
                        <li><code>GET /</code> - Main dashboard</li>
                        <li><code>GET /health</code> - Health check</li>
                        <li><code>POST /api/schedules</code> - Create medical schedules</li>
                        <li><code>GET /api/schedules</code> - List schedules</li>
                        <li><code>POST /api/appointments/reserve</code> - Reserve appointment</li>
                        <li><code>POST /api/appointments/cancel</code> - Cancel appointment</li>
                        <li><code>GET /api/docs</code> - API documentation</li>
                        <li><code>GET /api/test</code> - Interactive testing</li>
                    </ul>
                </div>
                
                <div class="feature-box">
                    <h3>🧪 Testing</h3>
                    <p>Run comprehensive tests:</p>
                    <div class="command">cd /Users/pramosba/gcp-IaC-PoC/tests && python run_tests.py</div>
                </div>
                
                <hr style="margin: 30px 0;">
                <a href="/apps" class="btn">← Back to App List</a>
                <a href="/" class="btn">Main Dashboard</a>
                <button onclick="startService()" class="btn" style="background: #2196f3;">🚀 Start Service</button>
            </div>
            
            <script>
                function startService() {
                    alert('To start the Medical Appointments API service:\\n\\n1. Open a new terminal\\n2. Run: cd /Users/pramosba/gcp-IaC-PoC/services\\n3. Run: python medical-appointments-service.py\\n\\nThe service will be available at http://localhost:8080');
                }
            </script>
        </body>
        </html>
        """)
        
    except Exception as e:
        return f"Error accessing Medical Appointments API: {str(e)}", 500
