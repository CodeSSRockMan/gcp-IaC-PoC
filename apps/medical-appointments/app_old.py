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
    'database': 'integrated_sql_firestore',
    'status': 'running',
    'gcp_integration': gcp_available
}

# ==== MODELS ====

class Schedule(db.Model):
    """Medical appointment schedule model"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    hour = db.Column(db.Time, nullable=False) 
    shared = db.Column(db.Boolean, default=False)
    reserved = db.Column(db.Boolean, default=False)
    reserved_by = db.Column(db.String(100), nullable=True)
    reserved_note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'hour': self.hour.strftime('%H:%M'),
            'shared': self.shared,
            'reserved': self.reserved,
            'reserved_by': self.reserved_by,
            'reserved_note': self.reserved_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def sync_to_firestore(self):
        """Sync appointment to Firestore for backup/analytics"""
        if gcp_available and firestore_db:
            try:
                firestore_db.collection('appointments').document(str(self.id)).set(self.to_dict())
                logger.info(f"Synced appointment {self.id} to Firestore")
            except Exception as e:
                logger.error(f"Failed to sync to Firestore: {e}")

# ==== UTILITY FUNCTIONS ====

def get_message(key, lang='en'):
    """Multi-language message system"""
    messages = {
        'en': {
            'invalid_date_format': 'Invalid date format. Use YYYY-MM-DD.',
            'invalid_hour_format': 'Invalid hour format. Use HH:MM.',
            'hour_out_of_range': 'Hour must be between 09:00 and 19:00.',
            'schedule_exists': 'A schedule already exists for this date and time.',
            'schedule_not_found': 'Schedule not found.',
            'schedule_created': 'Schedule created successfully.',
            'schedule_updated': 'Schedule updated successfully.',
            'schedule_deleted': 'Schedule deleted successfully.',
            'appointment_reserved': 'Appointment reserved successfully.',
            'appointment_cancelled': 'Appointment cancelled successfully.',
            'invalid_data': 'Invalid data provided.'
        },
        'es': {
            'invalid_date_format': 'Formato de fecha inválido. Use AAAA-MM-DD.',
            'invalid_hour_format': 'Formato de hora inválido. Use HH:MM.',
            'hour_out_of_range': 'La hora debe estar entre 09:00 y 19:00.',
            'schedule_exists': 'Ya existe un horario para esta fecha y hora.',
            'schedule_not_found': 'Horario no encontrado.',
            'schedule_created': 'Horario creado exitosamente.',
            'schedule_updated': 'Horario actualizado exitosamente.',
            'schedule_deleted': 'Horario eliminado exitosamente.',
            'appointment_reserved': 'Cita reservada exitosamente.',
            'appointment_cancelled': 'Cita cancelada exitosamente.',
            'invalid_data': 'Datos inválidos proporcionados.'
        }
    }
    return messages.get(lang, messages['en']).get(key, key)

def validate_hour(hour_str, lang='en'):
    """Validate hour format and range (09:00-19:00)"""
    try:
        hour_obj = datetime.strptime(hour_str, '%H:%M').time()
        if not (time(9, 0) <= hour_obj <= time(19, 0)):
            return False, None, 'hour_out_of_range'
        return True, hour_obj, None
    except (ValueError, TypeError):
        return False, None, 'invalid_hour_format'

def get_lang():
    """Get language from request header"""
    lang = request.headers.get('Accept-Language', 'en')
    return lang.lower() if lang.lower() in ['es', 'en'] else 'en'

# ==== HEALTH & STATUS ENDPOINTS ====

@app.route('/health')
def health():
    """Health check for auto-scaling"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
        
    return jsonify({
        'status': 'ok',
        'service': 'medical-appointments-api',
        'app_ready': True,
        'database_status': db_status,
        'gcp_available': gcp_available,
        'version': APP_CONFIG['version'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/configure', methods=['POST'])
def configure():
    """Configure service for auto-scaling infrastructure"""
    config = request.json or {}
    APP_CONFIG.update(config)
    logger.info(f"Service configured: {config}")
    return jsonify({'status': 'configured', 'config': APP_CONFIG})

@app.route('/deploy', methods=['POST'])
def deploy_app():
    """Deploy app configuration"""
    config = request.json or {}
    APP_CONFIG.update({
        'auto_scale': config.get('auto_scale', True),
        'storage_bucket': config.get('storage_bucket'),
        'database': config.get('database', 'integrated_sql_firestore'),
        'deployed_at': datetime.now().isoformat()
    })
    
    logger.info(f"Medical Appointments API deployed with config: {APP_CONFIG}")
    return jsonify({'status': 'deployed', 'config': APP_CONFIG})

# ==== MAIN DASHBOARD ====

@app.route('/')
def main_dashboard():
    """Main application dashboard"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Appointments API</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; color: #333;
            }
            .container { 
                max-width: 1200px; margin: 0 auto; 
                background: white; padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header { 
                color: #4285f4; border-bottom: 3px solid #4285f4; 
                padding-bottom: 15px; margin-bottom: 30px; text-align: center;
            }
            .feature-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; margin: 30px 0;
            }
            .feature { 
                padding: 20px; 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                border-radius: 10px; border-left: 5px solid #28a745;
                transition: transform 0.3s ease;
            }
            .feature:hover { transform: translateY(-5px); }
            .btn { 
                display: inline-block; padding: 12px 24px; 
                background: #28a745; color: white; 
                text-decoration: none; border-radius: 25px; 
                margin: 8px 5px; font-weight: 500;
                transition: all 0.3s ease;
            }
            .btn:hover { background: #218838; transform: translateY(-2px); }
            .btn-primary { background: #007bff; }
            .btn-primary:hover { background: #0056b3; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-info { background: #17a2b8; }
            .status { 
                display: inline-block; padding: 5px 10px; 
                border-radius: 15px; font-size: 0.9em; font-weight: bold;
            }
            .status.online { background: #d4edda; color: #155724; }
            .status.offline { background: #f8d7da; color: #721c24; }
            .stats-grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px; margin: 20px 0;
            }
            .stat-item {
                background: #f8f9fa; padding: 15px; border-radius: 8px;
                border-left: 4px solid #17a2b8; text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 Medical Appointments API</h1>
                <p>Auto-scaling Medical Appointment Management System</p>
                <span class="status {{ 'online' if gcp_available else 'offline' }}">
                    {{ '● GCP Auto-scaling Active' if gcp_available else '● Local Mode' }}
                </span>
            </div>
            
            <div class="feature-grid">
                <div class="feature">
                    <h3>📅 Schedule Management</h3>
                    <p>Create and manage medical appointment schedules</p>
                    <a href="/schedules" class="btn">View Schedules</a>
                    <a href="/schedules/create" class="btn btn-primary">Create Schedule</a>
                    <a href="/api/schedules" class="btn btn-info">API Endpoint</a>
                </div>
                
                <div class="feature">
                    <h3>🎯 Appointment Booking</h3>
                    <p>Reserve and manage patient appointments</p>
                    <a href="/appointments" class="btn">View Appointments</a>
                    <a href="/appointments/book" class="btn btn-primary">Book Appointment</a>
                    <a href="/api/appointments" class="btn btn-info">API Endpoint</a>
                </div>
                
                <div class="feature">
                    <h3>📊 Analytics Dashboard</h3>
                    <p>View appointment statistics and reports</p>
                    <a href="/analytics" class="btn">View Analytics</a>
                    <a href="/reports" class="btn btn-warning">Generate Reports</a>
                </div>
                
                <div class="feature">
                    <h3>🔧 API Documentation</h3>
                    <p>REST API endpoints and testing interface</p>
                    <a href="/api/docs" class="btn btn-info">API Docs</a>
                    <a href="/api/test" class="btn">Test API</a>
                    <a href="/api/status" class="btn">API Status</a>
                </div>
                
                <div class="feature">
                    <h3>⚙️ System Management</h3>
                    <p>System monitoring and configuration</p>
                    <a href="/admin" class="btn btn-warning">Admin Panel</a>
                    <a href="/health" class="btn btn-info">Health Check</a>
                    <a href="/logs" class="btn">View Logs</a>
                </div>
                
                <div class="feature">
                    <h3>🌐 Multi-language Support</h3>
                    <p>Available in English and Spanish</p>
                    <a href="/?lang=en" class="btn">English</a>
                    <a href="/?lang=es" class="btn">Español</a>
                </div>
            </div>
            
            <div class="feature">
                <h3>📈 System Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <strong>Version</strong><br>{{ version }}
                    </div>
                    <div class="stat-item">
                        <strong>Auto-scaling</strong><br>{{ 'Enabled' if auto_scale else 'Disabled' }}
                    </div>
                    <div class="stat-item">
                        <strong>Database</strong><br>{{ database_type }}
                    </div>
                    <div class="stat-item">
                        <strong>GCP Integration</strong><br>{{ 'Active' if gcp_available else 'Offline' }}
                    </div>
                    <div class="stat-item">
                        <strong>Deployed</strong><br>{{ deployed_time }}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """, 
    version=APP_CONFIG['version'],
    auto_scale=APP_CONFIG['auto_scale'],
    database_type=APP_CONFIG['database'],
    gcp_available=gcp_available,
    deployed_time=APP_CONFIG['deployed_at'][:19].replace('T', ' ')
    )

# ==== MEDICAL APPOINTMENTS API ROUTES ====

@app.route('/api/schedules', methods=['GET', 'POST'])
def api_schedules():
    """API endpoint for schedule management"""
    lang = get_lang()
    
    if request.method == 'POST':
        return create_schedule_api()
    else:
        return get_schedules_api()

def create_schedule_api():
    """Create a new schedule"""
    lang = get_lang()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': get_message('invalid_data', lang)}), 400
    
    date_str = data.get('date')
    hour_str = data.get('hour')
    shared = data.get('shared', False)

    # Validate date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'error': get_message('invalid_date_format', lang)}), 400

    # Validate hour
    is_valid, hour_obj, error_key = validate_hour(hour_str, lang)
    if not is_valid:
        return jsonify({'error': get_message(error_key, lang)}), 400

    # Check if schedule already exists
    existing = Schedule.query.filter_by(date=date_obj, hour=hour_obj).first()
    if existing:
        return jsonify({'error': get_message('schedule_exists', lang)}), 409

    # Create new schedule
    try:
        new_schedule = Schedule(date=date_obj, hour=hour_obj, shared=shared)
        db.session.add(new_schedule)
        db.session.commit()
        
        # Sync to Firestore for backup
        new_schedule.sync_to_firestore()
        
        return jsonify({
            'message': get_message('schedule_created', lang),
            'schedule': new_schedule.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating schedule: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def get_schedules_api():
    """Get all schedules with optional filtering"""
    try:
        # Get query parameters
        date_filter = request.args.get('date')
        shared_only = request.args.get('shared', '').lower() == 'true'
        available_only = request.args.get('available', '').lower() == 'true'
        
        # Build query
        query = Schedule.query
        
        if date_filter:
            try:
                date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter_by(date=date_obj)
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        
        if shared_only:
            query = query.filter_by(shared=True)
            
        if available_only:
            query = query.filter_by(reserved=False)
        
        schedules = query.order_by(Schedule.date, Schedule.hour).all()
        
        return jsonify({
            'schedules': [schedule.to_dict() for schedule in schedules],
            'count': len(schedules)
        })
    except Exception as e:
        logger.error(f"Error fetching schedules: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/schedules/<int:schedule_id>', methods=['GET', 'PUT', 'DELETE'])
def api_schedule_detail(schedule_id):
    """API endpoint for individual schedule management"""
    lang = get_lang()
    schedule = Schedule.query.get_or_404(schedule_id)
    
    if request.method == 'GET':
        return jsonify({'schedule': schedule.to_dict()})
    
    elif request.method == 'PUT':
        return update_schedule_api(schedule, lang)
    
    elif request.method == 'DELETE':
        return delete_schedule_api(schedule, lang)

def update_schedule_api(schedule, lang):
    """Update an existing schedule"""
    data = request.get_json()
    
    try:
        if 'shared' in data:
            schedule.shared = data['shared']
        
        schedule.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Sync to Firestore
        schedule.sync_to_firestore()
        
        return jsonify({
            'message': get_message('schedule_updated', lang),
            'schedule': schedule.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating schedule: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def delete_schedule_api(schedule, lang):
    """Delete a schedule"""
    try:
        # Delete from Firestore if available
        if gcp_available and firestore_db:
            try:
                firestore_db.collection('appointments').document(str(schedule.id)).delete()
            except Exception as e:
                logger.warning(f"Failed to delete from Firestore: {e}")
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({'message': get_message('schedule_deleted', lang)})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting schedule: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/appointments/reserve', methods=['POST'])
def reserve_appointment():
    """Reserve an appointment"""
    lang = get_lang()
    data = request.get_json()
    
    schedule_id = data.get('schedule_id')
    reserved_by = data.get('reserved_by')
    reserved_note = data.get('reserved_note', '')
    
    if not schedule_id or not reserved_by:
        return jsonify({'error': get_message('invalid_data', lang)}), 400
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    if schedule.reserved:
        return jsonify({'error': 'Appointment already reserved'}), 409
    
    try:
        schedule.reserved = True
        schedule.reserved_by = reserved_by
        schedule.reserved_note = reserved_note
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Sync to Firestore
        schedule.sync_to_firestore()
        
        return jsonify({
            'message': get_message('appointment_reserved', lang),
            'appointment': schedule.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error reserving appointment: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/appointments/cancel', methods=['POST'])
def cancel_appointment():
    """Cancel an appointment reservation"""
    lang = get_lang()
    data = request.get_json()
    
    schedule_id = data.get('schedule_id')
    schedule = Schedule.query.get_or_404(schedule_id)
    
    if not schedule.reserved:
        return jsonify({'error': 'Appointment is not reserved'}), 400
    
    try:
        schedule.reserved = False
        schedule.reserved_by = None
        schedule.reserved_note = None
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Sync to Firestore
        schedule.sync_to_firestore()
        
        return jsonify({
            'message': get_message('appointment_cancelled', lang),
            'appointment': schedule.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cancelling appointment: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ==== WEB INTERFACE ROUTES ====

@app.route('/schedules')
def schedules_page():
    """Web interface for viewing schedules"""
    try:
        schedules = Schedule.query.order_by(Schedule.date, Schedule.hour).limit(50).all()
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Medical Schedules</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .header { color: #28a745; border-bottom: 2px solid #28a745; padding-bottom: 10px; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #f8f9fa; font-weight: bold; }
                .btn { display: inline-block; padding: 8px 16px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; margin: 2px; }
                .btn-warning { background: #ffc107; color: #212529; }
                .btn-danger { background: #dc3545; }
                .status-reserved { color: #dc3545; font-weight: bold; }
                .status-available { color: #28a745; font-weight: bold; }
                .status-shared { background: #e3f2fd; padding: 2px 8px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">🏥 Medical Appointment Schedules</h1>
                <a href="/" class="btn">← Back to Dashboard</a>
                <a href="/schedules/create" class="btn">Create New Schedule</a>
                <a href="/api/schedules" class="btn btn-warning">API Endpoint</a>
                
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Status</th>
                            <th>Reserved By</th>
                            <th>Shared</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for schedule in schedules %}
                        <tr>
                            <td>{{ schedule.id }}</td>
                            <td>{{ schedule.date.strftime('%Y-%m-%d') }}</td>
                            <td>{{ schedule.hour.strftime('%H:%M') }}</td>
                            <td>
                                {% if schedule.reserved %}
                                    <span class="status-reserved">Reserved</span>
                                {% else %}
                                    <span class="status-available">Available</span>
                                {% endif %}
                            </td>
                            <td>{{ schedule.reserved_by or '-' }}</td>
                            <td>
                                {% if schedule.shared %}
                                    <span class="status-shared">Shared</span>
                                {% else %}
                                    Private
                                {% endif %}
                            </td>
                            <td>
                                <a href="/schedules/{{ schedule.id }}" class="btn" style="font-size: 12px; padding: 4px 8px;">View</a>
                                {% if not schedule.reserved %}
                                    <a href="/appointments/book/{{ schedule.id }}" class="btn btn-warning" style="font-size: 12px; padding: 4px 8px;">Book</a>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                {% if not schedules %}
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <h3>No schedules found</h3>
                        <p>Create your first medical appointment schedule!</p>
                        <a href="/schedules/create" class="btn">Create Schedule</a>
                    </div>
                {% endif %}
            </div>
        </body>
        </html>
        """, schedules=schedules)
    except Exception as e:
        logger.error(f"Error displaying schedules: {e}")
        return f"Error loading schedules: {str(e)}", 500

# ==== API DOCUMENTATION ====

@app.route('/api/docs')
def api_documentation():
    """API documentation interface"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Appointments API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .header { color: #17a2b8; border-bottom: 2px solid #17a2b8; padding-bottom: 10px; margin-bottom: 20px; }
            .endpoint { background: #f8f9fa; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; }
            .method { background: #007bff; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-right: 10px; }
            .method.post { background: #28a745; }
            .method.put { background: #ffc107; color: #212529; }
            .method.delete { background: #dc3545; }
            .code { background: #f4f4f4; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
            .btn { display: inline-block; padding: 8px 16px; background: #17a2b8; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🏥 Medical Appointments API Documentation</h1>
            <a href="/" class="btn">← Back to Dashboard</a>
            <a href="/api/test" class="btn">Test API</a>
            
            <h2>📋 Available Endpoints</h2>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p><strong>Description:</strong> Health check endpoint for auto-scaling</p>
                <p><strong>Response:</strong> Service status, database health, GCP availability</p>
                <div class="code">curl -X GET https://your-service-url/health</div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span> /api/schedules</h3>
                <p><strong>Description:</strong> Create a new medical appointment schedule</p>
                <p><strong>Parameters:</strong> date (YYYY-MM-DD), hour (HH:MM), shared (boolean)</p>
                <div class="code">curl -X POST https://your-service-url/api/schedules \\
  -H "Content-Type: application/json" \\
  -H "Accept-Language: en" \\
  -d '{"date": "2025-09-15", "hour": "14:30", "shared": true}'</div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /api/schedules</h3>
                <p><strong>Description:</strong> Get all schedules with optional filtering</p>
                <p><strong>Query Parameters:</strong> date, shared, available</p>
                <div class="code">curl -X GET "https://your-service-url/api/schedules?date=2025-09-15&available=true"</div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /api/schedules/{id}</h3>
                <p><strong>Description:</strong> Get specific schedule details</p>
                <div class="code">curl -X GET https://your-service-url/api/schedules/1</div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method put">PUT</span> /api/schedules/{id}</h3>
                <p><strong>Description:</strong> Update schedule (e.g., make shared/private)</p>
                <div class="code">curl -X PUT https://your-service-url/api/schedules/1 \\
  -H "Content-Type: application/json" \\
  -d '{"shared": true}'</div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method delete">DELETE</span> /api/schedules/{id}</h3>
                <p><strong>Description:</strong> Delete a schedule</p>
                <div class="code">curl -X DELETE https://your-service-url/api/schedules/1</div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span> /api/appointments/reserve</h3>
                <p><strong>Description:</strong> Reserve an appointment</p>
                <p><strong>Parameters:</strong> schedule_id, reserved_by, reserved_note (optional)</p>
                <div class="code">curl -X POST https://your-service-url/api/appointments/reserve \\
  -H "Content-Type: application/json" \\
  -d '{"schedule_id": 1, "reserved_by": "John Doe", "reserved_note": "Regular checkup"}'</div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span> /api/appointments/cancel</h3>
                <p><strong>Description:</strong> Cancel an appointment reservation</p>
                <div class="code">curl -X POST https://your-service-url/api/appointments/cancel \\
  -H "Content-Type: application/json" \\
  -d '{"schedule_id": 1}'</div>
            </div>
            
            <h2>🌐 Multi-language Support</h2>
            <p>Include <code>Accept-Language: es</code> header for Spanish responses, or <code>Accept-Language: en</code> for English (default).</p>
            
            <h2>🚀 Auto-scaling Features</h2>
            <ul>
                <li>✅ Automatic scaling from 0 to 10 instances based on demand</li>
                <li>✅ Health checks for load balancer integration</li>
                <li>✅ Firestore backup for appointment data</li>
                <li>✅ MySQL primary with SQLite fallback</li>
                <li>✅ CORS enabled for web applications</li>
            </ul>
        </div>
    </body>
    </html>
    """)

# ==== TEST ENDPOINTS ====

@app.route('/api/test')
def api_test_interface():
    """Interactive API testing interface"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Testing Interface</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .test-section { background: #f8f9fa; margin: 20px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
            .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #0056b3; }
            .result { background: #e9ecef; padding: 15px; border-radius: 4px; margin: 10px 0; font-family: monospace; white-space: pre-wrap; }
            .success { border-left: 4px solid #28a745; }
            .error { border-left: 4px solid #dc3545; }
            input, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Medical Appointments API Testing</h1>
            <a href="/api/docs" style="color: #007bff; text-decoration: none;">← Back to Documentation</a>
            
            <div class="test-section">
                <h3>Test 1: Health Check</h3>
                <button onclick="testHealth()" class="btn">Test Health Endpoint</button>
                <div id="health-result" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>Test 2: Create Schedule</h3>
                <input type="date" id="schedule-date" placeholder="Date">
                <input type="time" id="schedule-time" placeholder="Time (09:00-19:00)">
                <label><input type="checkbox" id="schedule-shared"> Shared with patients</label><br>
                <button onclick="testCreateSchedule()" class="btn">Create Schedule</button>
                <div id="create-result" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>Test 3: Get Schedules</h3>
                <button onclick="testGetSchedules()" class="btn">Get All Schedules</button>
                <button onclick="testGetSchedules('available=true')" class="btn">Get Available Only</button>
                <div id="get-result" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>Test 4: Reserve Appointment</h3>
                <input type="number" id="reserve-id" placeholder="Schedule ID">
                <input type="text" id="reserve-name" placeholder="Patient Name">
                <textarea id="reserve-note" placeholder="Notes (optional)" rows="2"></textarea>
                <button onclick="testReserve()" class="btn">Reserve Appointment</button>
                <div id="reserve-result" class="result" style="display: none;"></div>
            </div>
            
            <div id="global-results" style="margin-top: 30px;"></div>
        </div>
        
        <script>
            async function testHealth() {
                const resultDiv = document.getElementById('health-result');
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                    resultDiv.className = 'result success';
                } catch (error) {
                    resultDiv.textContent = 'Error: ' + error.message;
                    resultDiv.className = 'result error';
                }
                resultDiv.style.display = 'block';
            }
            
            async function testCreateSchedule() {
                const resultDiv = document.getElementById('create-result');
                const date = document.getElementById('schedule-date').value;
                const time = document.getElementById('schedule-time').value;
                const shared = document.getElementById('schedule-shared').checked;
                
                if (!date || !time) {
                    resultDiv.textContent = 'Please fill in date and time';
                    resultDiv.className = 'result error';
                    resultDiv.style.display = 'block';
                    return;
                }
                
                try {
                    const response = await fetch('/api/schedules', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ date, hour: time, shared })
                    });
                    const data = await response.json();
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                    resultDiv.className = response.ok ? 'result success' : 'result error';
                } catch (error) {
                    resultDiv.textContent = 'Error: ' + error.message;
                    resultDiv.className = 'result error';
                }
                resultDiv.style.display = 'block';
            }
            
            async function testGetSchedules(params = '') {
                const resultDiv = document.getElementById('get-result');
                try {
                    const url = '/api/schedules' + (params ? '?' + params : '');
                    const response = await fetch(url);
                    const data = await response.json();
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                    resultDiv.className = 'result success';
                } catch (error) {
                    resultDiv.textContent = 'Error: ' + error.message;
                    resultDiv.className = 'result error';
                }
                resultDiv.style.display = 'block';
            }
            
            async function testReserve() {
                const resultDiv = document.getElementById('reserve-result');
                const schedule_id = document.getElementById('reserve-id').value;
                const reserved_by = document.getElementById('reserve-name').value;
                const reserved_note = document.getElementById('reserve-note').value;
                
                if (!schedule_id || !reserved_by) {
                    resultDiv.textContent = 'Please fill in Schedule ID and Patient Name';
                    resultDiv.className = 'result error';
                    resultDiv.style.display = 'block';
                    return;
                }
                
                try {
                    const response = await fetch('/api/appointments/reserve', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ schedule_id: parseInt(schedule_id), reserved_by, reserved_note })
                    });
                    const data = await response.json();
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                    resultDiv.className = response.ok ? 'result success' : 'result error';
                } catch (error) {
                    resultDiv.textContent = 'Error: ' + error.message;
                    resultDiv.className = 'result error';
                }
                resultDiv.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """)

# Initialize database and start app
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    # Get port from environment (Cloud Run uses PORT env var)
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
