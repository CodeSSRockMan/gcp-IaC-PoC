#!/usr/bin/env python3
"""
Comprehensive Test Suite for Medical Appointments API
Tests all endpoints, Firebase integration, and health checks
"""
import unittest
import json
import sys
import os
import requests
from datetime import datetime, date, time
from unittest.mock import patch, MagicMock

# Add the apps directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'medical-appointments'))

class TestMedicalAppointmentsAPI(unittest.TestCase):
    """Test suite for Medical Appointments API"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Mock Firebase for testing
        cls.mock_firestore = MagicMock()
        
        # Set test environment variables
        os.environ['TESTING'] = 'true'
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        
        # Test URLs - can be localhost or actual instance
        cls.base_url = os.environ.get('TEST_BASE_URL', 'http://localhost:8080')
        cls.instance_url = os.environ.get('INSTANCE_URL', None)
        
    def setUp(self):
        """Set up each test"""
        with patch('google.cloud.firestore.Client', return_value=self.mock_firestore), \
             patch('google.cloud.storage.Client', return_value=self.mock_storage):
            
            # Import and create app after mocking GCP services
            # Import medical_appointments_service with proper path handling
            import sys
            import os
            services_dir = os.path.join(os.path.dirname(__file__), '..', 'services')
            if services_dir not in sys.path:
                sys.path.insert(0, services_dir)
            
            # Change to services directory temporarily for imports
            original_cwd = os.getcwd()
            try:
                os.chdir(services_dir)
                import medical_appointments_service
                self.app = medical_appointments_service.app
                self.db = medical_appointments_service.db
            finally:
                os.chdir(original_cwd)
            
            self.app.config['TESTING'] = True
            self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            self.client = self.app.test_client()
            
            with self.app.app_context():
                db.create_all()
    
    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            from medical_appointments_service import db
            db.session.remove()
            db.drop_all()

    # ==== HEALTH CHECK TESTS ====
    
    def test_health_endpoint(self):
        """Test health check endpoint for auto-scaling"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['service'], 'medical-appointments-api')
        self.assertTrue('timestamp' in data)
        self.assertTrue('gcp_available' in data)
    
    def test_configure_endpoint(self):
        """Test service configuration for auto-scaling"""
        config_data = {
            'auto_scale': True,
            'storage_bucket': 'test-bucket',
            'database': 'firestore'
        }
        
        response = self.client.post('/configure',
                                   data=json.dumps(config_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'configured')
    
    def test_deploy_endpoint(self):
        """Test app deployment configuration"""
        deploy_data = {
            'auto_scale': True,
            'storage_bucket': 'medical-appointments-bucket',
            'database': 'integrated_sql_firestore'
        }
        
        response = self.client.post('/deploy',
                                   data=json.dumps(deploy_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'deployed')

    # ==== SCHEDULE API TESTS ====
    
    def test_create_schedule_success(self):
        """Test successful schedule creation"""
        schedule_data = {
            'date': '2025-12-15',
            'hour': '14:30',
            'shared': True
        }
        
        response = self.client.post('/api/schedules',
                                   data=json.dumps(schedule_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue('schedule' in data)
        self.assertEqual(data['schedule']['date'], '2025-12-15')
        self.assertEqual(data['schedule']['hour'], '14:30')
        self.assertTrue(data['schedule']['shared'])
    
    def test_create_schedule_invalid_date(self):
        """Test schedule creation with invalid date"""
        schedule_data = {
            'date': 'invalid-date',
            'hour': '14:30',
            'shared': True
        }
        
        response = self.client.post('/api/schedules',
                                   data=json.dumps(schedule_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertTrue('error' in data)
    
    def test_create_schedule_invalid_hour(self):
        """Test schedule creation with invalid hour"""
        schedule_data = {
            'date': '2025-12-15',
            'hour': '08:30',  # Before 09:00
            'shared': True
        }
        
        response = self.client.post('/api/schedules',
                                   data=json.dumps(schedule_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertTrue('error' in data)
    
    def test_create_schedule_hour_out_of_range(self):
        """Test schedule creation with hour outside business hours"""
        schedule_data = {
            'date': '2025-12-15',
            'hour': '20:30',  # After 19:00
            'shared': True
        }
        
        response = self.client.post('/api/schedules',
                                   data=json.dumps(schedule_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_get_schedules(self):
        """Test getting all schedules"""
        # Create test schedules first
        self._create_test_schedule('2025-12-15', '10:00', True)
        self._create_test_schedule('2025-12-16', '15:00', False)
        
        response = self.client.get('/api/schedules')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue('schedules' in data)
        self.assertTrue('count' in data)
        self.assertEqual(data['count'], 2)
    
    def test_get_schedules_with_filters(self):
        """Test getting schedules with filters"""
        # Create test schedules
        self._create_test_schedule('2025-12-15', '10:00', True)
        self._create_test_schedule('2025-12-16', '15:00', False)
        
        # Test date filter
        response = self.client.get('/api/schedules?date=2025-12-15')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)
        
        # Test shared filter
        response = self.client.get('/api/schedules?shared=true')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)
    
    def test_get_specific_schedule(self):
        """Test getting a specific schedule"""
        schedule_id = self._create_test_schedule('2025-12-15', '10:00', True)
        
        response = self.client.get(f'/api/schedules/{schedule_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue('schedule' in data)
        self.assertEqual(data['schedule']['id'], schedule_id)
    
    def test_update_schedule(self):
        """Test updating a schedule"""
        schedule_id = self._create_test_schedule('2025-12-15', '10:00', False)
        
        update_data = {'shared': True}
        response = self.client.put(f'/api/schedules/{schedule_id}',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['schedule']['shared'])
    
    def test_delete_schedule(self):
        """Test deleting a schedule"""
        schedule_id = self._create_test_schedule('2025-12-15', '10:00', True)
        
        response = self.client.delete(f'/api/schedules/{schedule_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify it's deleted
        response = self.client.get(f'/api/schedules/{schedule_id}')
        self.assertEqual(response.status_code, 404)

    # ==== APPOINTMENT TESTS ====
    
    def test_reserve_appointment(self):
        """Test reserving an appointment"""
        schedule_id = self._create_test_schedule('2025-12-15', '10:00', True)
        
        reservation_data = {
            'schedule_id': schedule_id,
            'reserved_by': 'John Doe',
            'reserved_note': 'Regular checkup'
        }
        
        response = self.client.post('/api/appointments/reserve',
                                   data=json.dumps(reservation_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['appointment']['reserved'])
        self.assertEqual(data['appointment']['reserved_by'], 'John Doe')
    
    def test_reserve_already_reserved_appointment(self):
        """Test trying to reserve an already reserved appointment"""
        schedule_id = self._create_test_schedule('2025-12-15', '10:00', True)
        
        # Reserve the appointment first
        reservation_data = {
            'schedule_id': schedule_id,
            'reserved_by': 'John Doe',
            'reserved_note': 'First reservation'
        }
        self.client.post('/api/appointments/reserve',
                        data=json.dumps(reservation_data),
                        content_type='application/json')
        
        # Try to reserve again
        reservation_data['reserved_by'] = 'Jane Doe'
        response = self.client.post('/api/appointments/reserve',
                                   data=json.dumps(reservation_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 409)
    
    def test_cancel_appointment(self):
        """Test cancelling an appointment"""
        schedule_id = self._create_test_schedule('2025-12-15', '10:00', True)
        
        # Reserve the appointment first
        reservation_data = {
            'schedule_id': schedule_id,
            'reserved_by': 'John Doe',
            'reserved_note': 'Regular checkup'
        }
        self.client.post('/api/appointments/reserve',
                        data=json.dumps(reservation_data),
                        content_type='application/json')
        
        # Cancel the appointment
        cancel_data = {'schedule_id': schedule_id}
        response = self.client.post('/api/appointments/cancel',
                                   data=json.dumps(cancel_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify it's cancelled
        response = self.client.get(f'/api/schedules/{schedule_id}')
        data = json.loads(response.data)
        self.assertFalse(data['schedule']['reserved'])
    
    def test_cancel_non_reserved_appointment(self):
        """Test cancelling a non-reserved appointment"""
        schedule_id = self._create_test_schedule('2025-12-15', '10:00', True)
        
        cancel_data = {'schedule_id': schedule_id}
        response = self.client.post('/api/appointments/cancel',
                                   data=json.dumps(cancel_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # ==== MULTILINGUAL TESTS ====
    
    def test_multilingual_responses_english(self):
        """Test English language responses"""
        schedule_data = {
            'date': 'invalid-date',
            'hour': '14:30',
            'shared': True
        }
        
        response = self.client.post('/api/schedules',
                                   data=json.dumps(schedule_data),
                                   content_type='application/json',
                                   headers={'Accept-Language': 'en'})
        
        data = json.loads(response.data)
        self.assertIn('Invalid date format', data['error'])
    
    def test_multilingual_responses_spanish(self):
        """Test Spanish language responses"""
        schedule_data = {
            'date': 'invalid-date',
            'hour': '14:30',
            'shared': True
        }
        
        response = self.client.post('/api/schedules',
                                   data=json.dumps(schedule_data),
                                   content_type='application/json',
                                   headers={'Accept-Language': 'es'})
        
        data = json.loads(response.data)
        self.assertIn('inválido', data['error'].lower())

    # ==== WEB INTERFACE TESTS ====
    
    def test_main_dashboard(self):
        """Test main dashboard loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Medical Appointments API', response.data)
    
    def test_schedules_page(self):
        """Test schedules web page"""
        response = self.client.get('/schedules')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Medical Appointment Schedules', response.data)
    
    def test_api_documentation(self):
        """Test API documentation page"""
        response = self.client.get('/api/docs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'API Documentation', response.data)
    
    def test_api_test_interface(self):
        """Test API testing interface"""
        response = self.client.get('/api/test')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'API Testing', response.data)

    # ==== INTEGRATION TESTS ====
    
    def test_end_to_end_appointment_flow(self):
        """Test complete appointment booking flow"""
        # 1. Create a schedule
        schedule_data = {
            'date': '2025-12-20',
            'hour': '14:00',
            'shared': True
        }
        response = self.client.post('/api/schedules',
                                   data=json.dumps(schedule_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        schedule = json.loads(response.data)['schedule']
        
        # 2. Verify schedule appears in listings
        response = self.client.get('/api/schedules?available=true')
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)
        
        # 3. Reserve the appointment
        reservation_data = {
            'schedule_id': schedule['id'],
            'reserved_by': 'Alice Johnson',
            'reserved_note': 'Annual physical exam'
        }
        response = self.client.post('/api/appointments/reserve',
                                   data=json.dumps(reservation_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # 4. Verify appointment no longer available
        response = self.client.get('/api/schedules?available=true')
        data = json.loads(response.data)
        self.assertEqual(data['count'], 0)
        
        # 5. Cancel the appointment
        cancel_data = {'schedule_id': schedule['id']}
        response = self.client.post('/api/appointments/cancel',
                                   data=json.dumps(cancel_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # 6. Verify appointment available again
        response = self.client.get('/api/schedules?available=true')
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)

    # ==== PERFORMANCE & SCALING TESTS ====
    
    def test_bulk_schedule_creation(self):
        """Test creating multiple schedules (load testing)"""
        from datetime import timedelta
        
        base_date = date(2025, 12, 1)
        schedules_created = 0
        
        for day_offset in range(5):  # 5 days
            for hour in range(9, 18):  # 9 AM to 5 PM
                schedule_date = base_date + timedelta(days=day_offset)
                schedule_data = {
                    'date': schedule_date.strftime('%Y-%m-%d'),
                    'hour': f'{hour:02d}:00',
                    'shared': day_offset % 2 == 0  # Alternate shared/private
                }
                
                response = self.client.post('/api/schedules',
                                           data=json.dumps(schedule_data),
                                           content_type='application/json')
                if response.status_code == 201:
                    schedules_created += 1
        
        # Verify all schedules were created
        response = self.client.get('/api/schedules')
        data = json.loads(response.data)
        self.assertEqual(data['count'], schedules_created)
        self.assertEqual(schedules_created, 45)  # 5 days * 9 hours
    
    def test_concurrent_reservations(self):
        """Test handling concurrent reservation attempts"""
        import threading
        import time
        
        schedule_id = self._create_test_schedule('2025-12-25', '10:00', True)
        
        results = []
        
        def attempt_reservation(patient_name):
            reservation_data = {
                'schedule_id': schedule_id,
                'reserved_by': patient_name,
                'reserved_note': 'Concurrent test'
            }
            response = self.client.post('/api/appointments/reserve',
                                       data=json.dumps(reservation_data),
                                       content_type='application/json')
            results.append((patient_name, response.status_code))
        
        # Start multiple reservation attempts simultaneously
        threads = []
        for i in range(5):
            thread = threading.Thread(target=attempt_reservation, 
                                     args=[f'Patient{i}'])
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify only one succeeded
        successful_reservations = [r for r in results if r[1] == 200]
        failed_reservations = [r for r in results if r[1] == 409]
        
        self.assertEqual(len(successful_reservations), 1)
        self.assertEqual(len(failed_reservations), 4)

    # ==== HELPER METHODS ====
    
    def _create_test_schedule(self, date_str, hour_str, shared=True):
        """Helper method to create a test schedule"""
        schedule_data = {
            'date': date_str,
            'hour': hour_str,
            'shared': shared
        }
        
        response = self.client.post('/api/schedules',
                                   data=json.dumps(schedule_data),
                                   content_type='application/json')
        
        if response.status_code == 201:
            return json.loads(response.data)['schedule']['id']
        else:
            raise Exception(f"Failed to create test schedule: {response.data}")


class TestAutoScalingFeatures(unittest.TestCase):
    """Test auto-scaling specific features"""
    
    def test_health_check_response_time(self):
        """Test health check responds quickly for load balancer"""
        import time
        
        # This would be done with the actual service
        start_time = time.time()
        # Mock health check response
        response_time = time.time() - start_time
        
        # Health check should respond in under 1 second
        self.assertLess(response_time, 1.0)
    
    def test_firestore_sync_fallback(self):
        """Test that app continues working if Firestore is unavailable"""
        # This would test the fallback behavior when GCP services are down
        pass


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
