#!/usr/bin/env python3
"""
Entry Service - OpenStack-equivalent Gateway
Provides jumphost functionality and web interface
"""
import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Configuration from environment
API_ENDPOINT = os.getenv('API_ENDPOINT', 'http://localhost:8080')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'entry'})

@app.route('/')
def index():
    return render_template_string("""
    <html>
    <head><title>OpenStack-equivalent Gateway</title></head>
    <body>
        <h1>OpenStack-equivalent Gateway</h1>
        <h2>Available Services:</h2>
        <ul>
            <li><a href="/shell">Shell Access</a></li>
            <li><a href="/api">API Interface</a></li>
            <li><a href="/status">System Status</a></li>
        </ul>
    </body>
    </html>
    """)

@app.route('/shell')
def shell():
    """Basic shell interface (jumphost functionality)"""
    return render_template_string("""
    <html>
    <head><title>Shell Access</title></head>
    <body>
        <h1>Shell Access (Jumphost)</h1>
        <form method="post" action="/execute">
            <input type="text" name="command" placeholder="Enter command" size="50">
            <input type="submit" value="Execute">
        </form>
        <p><em>Basic commands: ls, ps, date, uptime</em></p>
    </body>
    </html>
    """)

@app.route('/execute', methods=['POST'])
def execute():
    """Execute basic commands via API"""
    command = request.form.get('command', '').strip()
    if command in ['ls', 'ps', 'date', 'uptime']:
        response = requests.post(f"{API_ENDPOINT}/execute", 
                               json={'command': command, 'source': 'entry'})
        return jsonify(response.json())
    return jsonify({'error': 'Command not allowed'})

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_api(path):
    """Proxy requests to API service"""
    url = f"{API_ENDPOINT}/{path}"
    headers = {'X-Forwarded-From': 'entry-service'}
    
    if request.method == 'GET':
        response = requests.get(url, headers=headers, params=request.args)
    elif request.method == 'POST':
        response = requests.post(url, headers=headers, json=request.json)
    elif request.method == 'PUT':
        response = requests.put(url, headers=headers, json=request.json)
    elif request.method == 'DELETE':
        response = requests.delete(url, headers=headers)
    
    return jsonify(response.json()) if response.content else '', response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
