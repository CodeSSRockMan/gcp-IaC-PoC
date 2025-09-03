#!/usr/bin/env python3
"""
API Service - OpenStack-equivalent Controller
Validates requests and manages access to compute resources
"""
import os
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration
COMPUTE_ENDPOINT = os.getenv('COMPUTE_ENDPOINT', 'http://localhost:8081')
ALLOWED_SOURCES = ['entry-service']

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'api'})

@app.route('/configure', methods=['POST'])
def configure():
    """Configure API service with endpoints"""
    config = request.json
    app.logger.info(f"API service configured: {config}")
    return jsonify({'status': 'configured'})

def validate_request():
    """Validate request source"""
    forwarded_from = request.headers.get('X-Forwarded-From')
    if forwarded_from not in ALLOWED_SOURCES:
        app.logger.warning(f"Unauthorized access attempt from: {forwarded_from}")
        return False
    return True

def log_request(action, data=None):
    """Log API requests"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'action': action,
        'source': request.headers.get('X-Forwarded-From'),
        'data': data
    }
    app.logger.info(f"API Request: {log_entry}")

@app.route('/execute', methods=['POST'])
def execute():
    """Execute commands via compute service"""
    if not validate_request():
        return jsonify({'error': 'Unauthorized'}), 403
    
    command_data = request.json
    log_request('execute_command', command_data)
    
    # Forward to compute service
    response = requests.post(f"{COMPUTE_ENDPOINT}/execute", 
                           json=command_data,
                           headers={'X-Forwarded-From': 'api-service'})
    
    return jsonify(response.json()), response.status_code

@app.route('/storage/<action>', methods=['GET', 'POST'])
def storage_action(action):
    """Handle storage operations"""
    if not validate_request():
        return jsonify({'error': 'Unauthorized'}), 403
    
    log_request(f'storage_{action}', request.json)
    
    # Forward to compute service for storage operations
    response = requests.request(
        request.method,
        f"{COMPUTE_ENDPOINT}/storage/{action}",
        json=request.json,
        headers={'X-Forwarded-From': 'api-service'}
    )
    
    return jsonify(response.json()), response.status_code

@app.route('/compute/<path:path>', methods=['GET', 'POST'])
def compute_proxy(path):
    """Proxy requests to compute service"""
    if not validate_request():
        return jsonify({'error': 'Unauthorized'}), 403
    
    log_request(f'compute_{path}', request.json)
    
    response = requests.request(
        request.method,
        f"{COMPUTE_ENDPOINT}/{path}",
        json=request.json,
        headers={'X-Forwarded-From': 'api-service'}
    )
    
    return jsonify(response.json()), response.status_code

@app.route('/test-compute')
def test_compute():
    """Test connectivity to compute service"""
    try:
        response = requests.get(f"{COMPUTE_ENDPOINT}/health", timeout=5)
        return jsonify({'compute_status': 'ok', 'response': response.json()})
    except Exception as e:
        return jsonify({'compute_status': 'error', 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
