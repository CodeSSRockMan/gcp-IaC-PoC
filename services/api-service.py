#!/usr/bin/env python3
"""
API Service - Request Controller and Validator
Manages access and communication between entry and compute services
"""
import os
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration
COMPUTE_ENDPOINT = os.getenv('COMPUTE_ENDPOINT', 'http://localhost:8080')

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok', 
        'service': 'api',
        'timestamp': datetime.now().isoformat(),
        'compute_endpoint': COMPUTE_ENDPOINT
    })

@app.route('/configure', methods=['POST'])
def configure():
    """Configure API service with endpoints"""
    config = request.json or {}
    global COMPUTE_ENDPOINT
    COMPUTE_ENDPOINT = config.get('compute_endpoint', COMPUTE_ENDPOINT)
    app.logger.info(f"API service configured: compute_endpoint={COMPUTE_ENDPOINT}")
    return jsonify({'status': 'configured', 'compute_endpoint': COMPUTE_ENDPOINT})

def log_request(action, data=None):
    """Log API requests"""
    timestamp = datetime.now().isoformat()
    source = request.headers.get('X-Forwarded-From', 'unknown')
    app.logger.info(f"API Request [{timestamp}]: {action} from {source}")

@app.route('/shell')
@app.route('/shell/<path:path>')
def shell_proxy(path=''):
    """Proxy shell requests to compute service with security"""
    log_request('shell_access', {'path': path})
    
    try:
        target_url = f"{COMPUTE_ENDPOINT}/shell/{path}" if path else f"{COMPUTE_ENDPOINT}/shell"
        
        resp = requests.get(
            target_url,
            params=request.args,
            headers={'X-Forwarded-From': 'api-service'},
            timeout=30
        )
        
        return resp.content, resp.status_code, resp.headers.items()
        
    except requests.RequestException as e:
        app.logger.error(f"Shell proxy error: {e}")
        return jsonify({'error': 'Shell service unavailable'}), 503

@app.route('/compute/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def compute_proxy(path):
    """Proxy requests to compute service"""
    log_request('compute_request', {'path': path, 'method': request.method})
    
    try:
        target_url = f"{COMPUTE_ENDPOINT}/{path}"
        
        if request.method == 'GET':
            resp = requests.get(target_url, params=request.args, timeout=30)
        elif request.method == 'POST':
            resp = requests.post(target_url, json=request.json, timeout=30)
        elif request.method == 'PUT':
            resp = requests.put(target_url, json=request.json, timeout=30)
        elif request.method == 'DELETE':
            resp = requests.delete(target_url, timeout=30)
        
        return resp.content, resp.status_code, resp.headers.items()
        
    except requests.RequestException as e:
        app.logger.error(f"Compute proxy error: {e}")
        return jsonify({'error': 'Compute service unavailable'}), 503

@app.route('/status')
def api_status():
    """Extended API status"""
    try:
        # Check compute service
        compute_resp = requests.get(f"{COMPUTE_ENDPOINT}/health", timeout=5)
        compute_status = compute_resp.json()
    except:
        compute_status = {'status': 'error', 'error': 'unreachable'}
    
    return jsonify({
        'service': 'api',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'compute_endpoint': COMPUTE_ENDPOINT,
        'compute_service': compute_status,
        'request_count': getattr(app, 'request_count', 0)
    })

@app.before_request
def before_request():
    """Log all requests"""
    if not hasattr(app, 'request_count'):
        app.request_count = 0
    app.request_count += 1

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=False)
