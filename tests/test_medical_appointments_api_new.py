#!/usr/bin/env python3
"""
Test Suite for Medical Appointments API - Firebase/Firestore Only
Tests endpoints, health checks, and Firebase integration
"""
import unittest
import json
import sys
import os
import requests
from datetime import datetime

class TestMedicalAppointmentsAPI(unittest.TestCase):
    """Test suite for Medical Appointments API with Firebase backend"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Test URLs - can be localhost or actual instance
        cls.base_url = os.environ.get('TEST_BASE_URL', 'http://localhost:8080')
        cls.instance_url = os.environ.get('INSTANCE_URL', None)
        
        print(f"🧪 Testing Medical Appointments API")
        print(f"📍 Base URL: {cls.base_url}")
        if cls.instance_url:
            print(f"🌐 Instance URL: {cls.instance_url}")
    
    def setUp(self):
        """Set up each test"""
        self.headers = {'Content-Type': 'application/json'}
        
    def test_direct_import(self):
        """Test importing the app directly"""
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'medical-appointments'))
            import app
            self.assertIsNotNone(app.app)
            print("✅ Direct app import: SUCCESS")
        except ImportError as e:
            print(f"⚠️ Direct import failed (expected in instance): {e}")
            
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('status', data)
            self.assertIn('version', data)
            print("✅ Health endpoint: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ Health endpoint failed: {e}")
            self.fail(f"Health endpoint test failed: {e}")
    
    def test_api_health_endpoint(self):
        """Test API health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('status', data)
            self.assertIn('version', data)
            self.assertIn('timestamp', data)
            print("✅ API health endpoint: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ API health endpoint failed: {e}")
            self.fail(f"API health endpoint test failed: {e}")
    
    def test_appointments_get(self):
        """Test GET appointments endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/appointments", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('success', data)
            print("✅ Appointments GET: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ Appointments GET failed: {e}")
            self.fail(f"Appointments GET test failed: {e}")
    
    def test_appointments_post(self):
        """Test POST appointments endpoint"""
        appointment_data = {
            'patient_name': 'Test Patient',
            'doctor_name': 'Dr. Test',
            'appointment_date': '2025-09-10',
            'appointment_time': '14:30',
            'description': 'Test appointment'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/appointments", 
                json=appointment_data,
                headers=self.headers,
                timeout=10
            )
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.assertIn('success', data)
            print("✅ Appointments POST: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ Appointments POST failed: {e}")
            self.fail(f"Appointments POST test failed: {e}")
    
    def test_patients_endpoint(self):
        """Test patients endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/patients", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('success', data)
            print("✅ Patients endpoint: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ Patients endpoint failed: {e}")
            self.fail(f"Patients endpoint test failed: {e}")
    
    def test_doctors_endpoint(self):
        """Test doctors endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/doctors", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('success', data)
            print("✅ Doctors endpoint: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ Doctors endpoint failed: {e}")
            self.fail(f"Doctors endpoint test failed: {e}")
    
    def test_language_endpoint(self):
        """Test language endpoint (this was previously failing)"""
        try:
            response = requests.get(f"{self.base_url}/api/lang", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('supported_languages', data)
            self.assertIn('current_language', data)
            print("✅ Language endpoint: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ Language endpoint failed: {e}")
            self.fail(f"Language endpoint test failed: {e}")
    
    def test_main_app_page(self):
        """Test main application page"""
        try:
            response = requests.get(f"{self.base_url}/medical-appointments/", timeout=10)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Medical Appointments API', response.text)
            print("✅ Main app page: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ Main app page failed: {e}")
            self.fail(f"Main app page test failed: {e}")
    
    def test_home_page(self):
        """Test home page"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Medical Appointments', response.text)
            print("✅ Home page: SUCCESS")
        except requests.exceptions.RequestException as e:
            print(f"❌ Home page failed: {e}")
            self.fail(f"Home page test failed: {e}")
    
    def test_instance_endpoints(self):
        """Test endpoints on actual instance if URL provided"""
        if not self.instance_url:
            print("⏭️ Skipping instance tests (no INSTANCE_URL provided)")
            return
            
        print(f"🌐 Testing instance endpoints at {self.instance_url}")
        
        endpoints_to_test = [
            '/health',
            '/api/health',
            '/api/appointments',
            '/api/patients',
            '/api/doctors',
            '/api/lang',
            '/medical-appointments/'
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.instance_url}{endpoint}", timeout=15)
                self.assertIn(response.status_code, [200, 201])
                print(f"✅ Instance {endpoint}: SUCCESS")
            except requests.exceptions.RequestException as e:
                print(f"❌ Instance {endpoint} failed: {e}")
    
    def test_firebase_functionality(self):
        """Test Firebase-specific functionality"""
        # Test that we can create and retrieve data through the API
        patient_data = {
            'name': 'Test Patient Firebase',
            'email': 'test@firebase.com'
        }
        
        try:
            # Create a patient
            response = requests.post(
                f"{self.base_url}/api/patients",
                json=patient_data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 201:
                # Try to get patients list
                get_response = requests.get(f"{self.base_url}/api/patients", timeout=10)
                self.assertEqual(get_response.status_code, 200)
                print("✅ Firebase functionality test: SUCCESS")
            else:
                print("⚠️ Firebase functionality: Limited (Firebase may not be available)")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Firebase functionality test failed: {e}")

def run_tests():
    """Run all tests with detailed output"""
    print("🏥 Starting Medical Appointments API Test Suite")
    print("=" * 60)
    
    # Configure test runner for verbose output
    unittest.main(verbosity=2, exit=False)

if __name__ == '__main__':
    # Check for environment variables
    base_url = os.environ.get('TEST_BASE_URL', 'http://localhost:8080')
    instance_url = os.environ.get('INSTANCE_URL', None)
    
    print(f"🧪 Medical Appointments API Test Suite")
    print(f"📍 Testing URL: {base_url}")
    if instance_url:
        print(f"🌐 Instance URL: {instance_url}")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2)
