#!/usr/bin/env python3
"""
Entry Service - Gateway and Load Balancer
Provides public access point and routes to your Python app
"""
import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, redirect

app = Flask(__name__)

# Configuration from environment
API_ENDPOINT = os.getenv('API_ENDPOINT', 'http://localhost:8081')
COMPUTE_ENDPOINT = os.getenv('COMPUTE_ENDPOINT', 'http://localhost:8080')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'entry'})

@app.route('/configure', methods=['POST'])
def configure():
    """Configure entry service"""
    config = request.json or {}
    global API_ENDPOINT, COMPUTE_ENDPOINT
    API_ENDPOINT = config.get('api_endpoint', API_ENDPOINT)
    COMPUTE_ENDPOINT = config.get('compute_endpoint', COMPUTE_ENDPOINT)
    app.logger.info(f"Entry service configured: API={API_ENDPOINT}, COMPUTE={COMPUTE_ENDPOINT}")
    return jsonify({'status': 'configured'})

@app.route('/')
def index():
    """Main landing page with app access"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Python App Gateway</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; padding: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                min-height: 100vh;
            }
            .container { 
                max-width: 1000px; margin: 0 auto; 
                background: rgba(255,255,255,0.15); 
                padding: 40px; border-radius: 20px; 
                backdrop-filter: blur(15px); 
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            }
            .header { text-align: center; margin-bottom: 50px; }
            .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .service-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 30px; 
                margin: 40px 0;
            }
            .service-card { 
                background: rgba(255,255,255,0.2); 
                padding: 30px; border-radius: 15px; 
                text-align: center; 
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .service-card:hover { 
                transform: translateY(-10px); 
                background: rgba(255,255,255,0.25);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            .service-icon { 
                font-size: 3em; 
                margin-bottom: 20px; 
                display: block;
            }
            .btn { 
                display: inline-block; 
                padding: 15px 30px; 
                background: rgba(255,255,255,0.9); 
                color: #333; 
                text-decoration: none; 
                border-radius: 30px; 
                margin: 15px 10px; 
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .btn:hover { 
                background: white; 
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }
            .btn-primary { background: #4285f4; color: white; }
            .btn-success { background: #34a853; color: white; }
            .btn-warning { background: #fbbc04; color: #333; }
            .btn-info { background: #00acc1; color: white; }
            .status-banner {
                background: rgba(52, 168, 83, 0.2);
                border: 1px solid rgba(52, 168, 83, 0.5);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Python App Gateway</h1>
                <p style="font-size: 1.2em; opacity: 0.9;">OpenStack-equivalent Serverless Infrastructure</p>
            </div>
            
            <div class="status-banner">
                <strong>✓ System Status:</strong> All services operational | 
                <strong>Gateway:</strong> Active | 
                <strong>Auto-scaling:</strong> Enabled
            </div>
            
            <div class="service-grid">
                <div class="service-card">
                    <span class="service-icon">📱</span>
                    <h2>Your Python App</h2>
                    <p>Access your deployed Python application with full UI and functionality</p>
                    <a href="/app" class="btn btn-primary">Launch Application</a>
                </div>
                
                <div class="service-card">
                    <span class="service-icon">🔧</span>
                    <h2>Shell Access</h2>
                    <p>Command line interface and system administration tools</p>
                    <a href="/shell" class="btn btn-info">Open Terminal</a>
                </div>
                
                <div class="service-card">
                    <span class="service-icon">📊</span>
                    <h2>API Interface</h2>
                    <p>Direct API access, monitoring, and system integration</p>
                    <a href="/api/status" class="btn btn-success">API Dashboard</a>
                </div>
                
                <div class="service-card">
                    <span class="service-icon">⚡</span>
                    <h2>System Monitor</h2>
                    <p>Infrastructure health, metrics, and performance data</p>
                    <a href="/status" class="btn btn-warning">View Metrics</a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px; opacity: 0.8;">
                <p>Powered by Google Cloud Platform • Auto-scaling Cloud Run Services</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route('/app')
@app.route('/app/<path:path>')
def python_app(path=''):
    """Route to your Python application"""
    try:
        # Direct proxy to compute service
        target_url = f"{COMPUTE_ENDPOINT}/{path}"
        
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
        
        # Return the response from compute service
        return resp.content, resp.status_code, resp.headers.items()
        
    except requests.RequestException as e:
        app.logger.error(f"Failed to proxy to compute service: {e}")
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Service Unavailable</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; text-align: center; background: #f5f5f5; }
                .error-container { 
                    max-width: 600px; margin: 0 auto; 
                    background: white; padding: 40px; 
                    border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                .error-icon { font-size: 4em; color: #ea4335; margin-bottom: 20px; }
                .btn { 
                    display: inline-block; padding: 12px 24px; 
                    background: #4285f4; color: white; 
                    text-decoration: none; border-radius: 5px; 
                    margin: 10px;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h1>Python App Temporarily Unavailable</h1>
                <p>The compute service is starting up or temporarily unavailable.</p>
                <p>Please try again in a few moments.</p>
                <a href="/" class="btn">← Back to Gateway</a>
                <a href="/status" class="btn">Check Status</a>
            </div>
        </body>
        </html>
        """), 503

@app.route('/shell')
@app.route('/shell/<path:path>')
def shell_access(path=''):
    """Route to shell interface via API service"""
    try:
        # Route through API service for security
        target_url = f"{API_ENDPOINT}/shell/{path}" if path else f"{API_ENDPOINT}/shell"
        
        resp = requests.get(
            target_url, 
            params=request.args,
            headers={'X-Forwarded-From': 'entry-service'},
            timeout=30
        )
        
        return resp.content, resp.status_code, resp.headers.items()
        
    except requests.RequestException as e:
        return jsonify({'error': f'Shell service unavailable: {str(e)}'}), 503

@app.route('/api/status')
def api_status():
    """Get system status from all services"""
    status = {
        'gateway': {'status': 'ok', 'service': 'entry'},
        'api': {'status': 'unknown'},
        'compute': {'status': 'unknown'},
        'timestamp': datetime.now().isoformat() if 'datetime' in globals() else 'unknown'
    }
    
    # Check API service
    try:
        resp = requests.get(f"{API_ENDPOINT}/health", timeout=5)
        status['api'] = resp.json()
    except:
        status['api'] = {'status': 'error', 'error': 'unreachable'}
    
    # Check compute service
    try:
        resp = requests.get(f"{COMPUTE_ENDPOINT}/health", timeout=5)
        status['compute'] = resp.json()
    except:
        status['compute'] = {'status': 'error', 'error': 'unreachable'}
    
    return jsonify(status)

@app.route('/status')
def system_status():
    """System status dashboard"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Status</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; padding: 20px; 
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }
            .container { 
                max-width: 1000px; margin: 0 auto; 
                background: white; padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .header { 
                color: #4285f4; 
                border-bottom: 3px solid #4285f4; 
                padding-bottom: 15px; 
                margin-bottom: 30px;
            }
            .service-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
                margin: 30px 0;
            }
            .service-status { 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 10px; 
                border-left: 5px solid #28a745;
            }
            .service-status.error { border-left-color: #dc3545; }
            .service-status.warning { border-left-color: #ffc107; }
            .btn { 
                display: inline-block; 
                padding: 10px 20px; 
                background: #4285f4; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 5px;
            }
            .status-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-ok { background: #28a745; }
            .status-error { background: #dc3545; }
            .status-unknown { background: #6c757d; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🖥️ System Status Dashboard</h1>
                <p>Real-time infrastructure monitoring</p>
            </div>
            
            <a href="/" class="btn">← Back to Gateway</a>
            <button onclick="location.reload()" class="btn">🔄 Refresh</button>
            
            <div class="service-grid" id="status-grid">
                <div class="service-status">
                    <h3><span class="status-indicator status-ok"></span>Gateway Service</h3>
                    <p><strong>Status:</strong> Operational</p>
                    <p><strong>Role:</strong> Load balancer and entry point</p>
                    <p><strong>Uptime:</strong> Active</p>
                </div>
                
                <div class="service-status" id="api-status">
                    <h3><span class="status-indicator status-unknown"></span>API Service</h3>
                    <p><strong>Status:</strong> <span id="api-status-text">Checking...</span></p>
                    <p><strong>Role:</strong> Request controller and validator</p>
                    <p><strong>Endpoint:</strong> {{ api_endpoint }}</p>
                </div>
                
                <div class="service-status" id="compute-status">
                    <h3><span class="status-indicator status-unknown"></span>Compute Service</h3>
                    <p><strong>Status:</strong> <span id="compute-status-text">Checking...</span></p>
                    <p><strong>Role:</strong> Python application server</p>
                    <p><strong>Endpoint:</strong> {{ compute_endpoint }}</p>
                </div>
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 10px;">
                <h3>🔗 Service Endpoints</h3>
                <ul>
                    <li><strong>Gateway:</strong> This service (entry point)</li>
                    <li><strong>API Service:</strong> {{ api_endpoint }}</li>
                    <li><strong>Compute Service:</strong> {{ compute_endpoint }}</li>
                </ul>
            </div>
        </div>
        
        <script>
            async function checkStatus() {
                try {
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    
                    // Update API status
                    const apiIndicator = document.querySelector('#api-status .status-indicator');
                    const apiText = document.getElementById('api-status-text');
                    if (status.api.status === 'ok') {
                        apiIndicator.className = 'status-indicator status-ok';
                        apiText.textContent = 'Operational';
                    } else {
                        apiIndicator.className = 'status-indicator status-error';
                        apiText.textContent = 'Error: ' + (status.api.error || 'unknown');
                    }
                    
                    // Update Compute status
                    const computeIndicator = document.querySelector('#compute-status .status-indicator');
                    const computeText = document.getElementById('compute-status-text');
                    if (status.compute.status === 'ok') {
                        computeIndicator.className = 'status-indicator status-ok';
                        computeText.textContent = 'Operational';
                    } else {
                        computeIndicator.className = 'status-indicator status-error';
                        computeText.textContent = 'Error: ' + (status.compute.error || 'unknown');
                    }
                } catch (error) {
                    console.error('Failed to fetch status:', error);
                }
            }
            
            // Check status on load and every 30 seconds
            checkStatus();
            setInterval(checkStatus, 30000);
        </script>
    </body>
    </html>
    """, api_endpoint=API_ENDPOINT, compute_endpoint=COMPUTE_ENDPOINT)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8082))
    app.run(host='0.0.0.0', port=port, debug=False)
        # Forward request to compute service (your app)
        url = f"{API_ENDPOINT}/app/{path}" if path else f"{API_ENDPOINT}/app"
        
        if request.method == 'GET':
            response = requests.get(url, params=request.args, timeout=30)
        else:
            response = requests.request(
                request.method, 
                url, 
                json=request.json,
                data=request.form,
                files=request.files,
                timeout=30
            )
        
        # Return the response from your app
        if response.headers.get('content-type', '').startswith('text/html'):
            return response.text, response.status_code
        else:
            return jsonify(response.json()), response.status_code
            
    except requests.exceptions.RequestException as e:
        return render_template_string("""
        <html>
        <body style="font-family: Arial; margin: 40px; text-align: center;">
            <h1>🚧 App Starting Up</h1>
            <p>Your Python app is initializing. Please wait a moment and refresh.</p>
            <a href="/" style="color: #4285f4;">← Back to Gateway</a>
            <br><br>
            <small>Error: {{ error }}</small>
        </body>
        </html>
        """, error=str(e))

@app.route('/shell')
def shell():
    """Shell interface for system access"""
    return render_template_string("""
    <html>
    <head>
        <title>Shell Access</title>
        <style>
            body { font-family: 'Courier New', monospace; margin: 20px; background: #1e1e1e; color: #00ff00; }
            .terminal { background: #000; padding: 20px; border-radius: 5px; min-height: 400px; }
            .prompt { color: #00ff00; }
            .output { color: #ffffff; margin: 10px 0; }
            input[type="text"] { background: transparent; border: none; color: #00ff00; font-family: 'Courier New'; width: 70%; }
            .btn { background: #333; color: #00ff00; border: 1px solid #00ff00; padding: 5px 15px; }
        </style>
    </head>
    <body>
        <h1>🖥️ Shell Access (Jumphost)</h1>
        <a href="/" style="color: #4285f4;">← Back to Gateway</a>
        
        <div class="terminal">
            <div class="prompt">user@python-app-gateway:~$ </div>
            <div id="output"></div>
            
            <form onsubmit="executeCommand(event)">
                <span class="prompt">user@python-app-gateway:~$ </span>
                <input type="text" id="command" placeholder="Enter command (status, uptime, ps, app-stats)" autofocus>
                <input type="submit" value="Execute" class="btn">
            </form>
        </div>
        
        <script>
        function executeCommand(event) {
            event.preventDefault();
            const command = document.getElementById('command').value;
            const output = document.getElementById('output');
            
            // Add command to output
            output.innerHTML += '<div class="output">user@python-app-gateway:~$ ' + command + '</div>';
            
            // Execute via API
            fetch('/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command})
            })
            .then(r => r.json())
            .then(data => {
                if (data.output) {
                    output.innerHTML += '<div class="output">' + data.output.replace(/\\n/g, '<br>') + '</div>';
                } else if (data.result) {
                    output.innerHTML += '<div class="output">' + JSON.stringify(data.result, null, 2) + '</div>';
                } else if (data.error) {
                    output.innerHTML += '<div class="output" style="color: #ff6b6b;">Error: ' + data.error + '</div>';
                }
                output.scrollTop = output.scrollHeight;
            })
            .catch(err => {
                output.innerHTML += '<div class="output" style="color: #ff6b6b;">Network error: ' + err + '</div>';
            });
            
            document.getElementById('command').value = '';
        }
        </script>
    </body>
    </html>
    """)

@app.route('/execute', methods=['POST'])
def execute():
    """Execute commands through API service"""
    command = request.json.get('command', '').strip()
    
    # Basic gateway commands
    if command == 'status':
        return jsonify({'result': {'gateway': 'running', 'api_endpoint': API_ENDPOINT}})
    elif command == 'help':
        return jsonify({'result': 'Available: status, uptime, ps, app-stats, help'})
    
    # Forward other commands to API service
    try:
        response = requests.post(f"{API_ENDPOINT}/execute", 
                               json={'command': command, 'source': 'gateway'},
                               headers={'X-Forwarded-From': 'entry-service'},
                               timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': f'Cannot reach backend: {str(e)}'})

@app.route('/status')
def system_status():
    """System status page"""
    try:
        # Check API service
        api_response = requests.get(f"{API_ENDPOINT}/health", timeout=5)
        api_status = "🟢 Online" if api_response.status_code == 200 else "🔴 Offline"
        
        # Check app status
        app_response = requests.get(f"{API_ENDPOINT}/app/api/status", timeout=5)
        app_status = "🟢 Running" if app_response.status_code == 200 else "🔴 Offline"
        
    except:
        api_status = "🔴 Offline"
        app_status = "🔴 Offline"
    
    return render_template_string("""
    <html>
    <head><title>System Status</title></head>
    <body style="font-family: Arial; margin: 40px;">
        <h1>📊 System Status</h1>
        <a href="/" style="color: #4285f4;">← Back to Gateway</a>
        
        <div style="margin: 30px 0;">
            <h3>Service Health:</h3>
            <p><strong>Entry Gateway:</strong> 🟢 Online (you're here!)</p>
            <p><strong>API Controller:</strong> {{ api_status }}</p>
            <p><strong>Python App:</strong> {{ app_status }}</p>
        </div>
        
        <div style="margin: 30px 0;">
            <h3>Quick Actions:</h3>
            <a href="/app" style="padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">Access App</a>
            <a href="/shell" style="padding: 10px 20px; background: #34a853; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">Open Shell</a>
            <a href="/api/status" style="padding: 10px 20px; background: #fbbc04; color: black; text-decoration: none; border-radius: 5px; margin: 5px;">API Details</a>
        </div>
    </body>
    </html>
    """, api_status=api_status, app_status=app_status)

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_api(path):
    """Proxy API requests"""
    url = f"{API_ENDPOINT}/{path}"
    headers = {'X-Forwarded-From': 'entry-service'}
    
    try:
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args, timeout=10)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.json, timeout=10)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.json, timeout=10)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        
        return jsonify(response.json()) if response.content else '', response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
