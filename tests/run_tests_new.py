#!/usr/bin/env python3
"""
Test Runner for Medical Appointments API
Runs comprehensive tests for the Firebase-only medical appointments system
"""
import os
import sys
import subprocess
import unittest
import requests
from datetime import datetime

def check_app_availability():
    """Check if the app is running locally or on instance"""
    print("🔍 Checking app availability...")
    
    local_url = "http://localhost:8080"
    instance_url = os.environ.get('INSTANCE_URL')
    
    # Test local
    try:
        response = requests.get(f"{local_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Local app available at {local_url}")
            return local_url
    except:
        print("❌ Local app not available")
    
    # Test instance if provided
    if instance_url:
        try:
            response = requests.get(f"{instance_url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ Instance app available at {instance_url}")
                return instance_url
        except:
            print(f"❌ Instance app not available at {instance_url}")
    
    return None

def run_local_app():
    """Try to run the app locally for testing"""
    print("🚀 Attempting to start local app for testing...")
    
    app_path = os.path.join(os.path.dirname(__file__), '..', 'apps', 'medical-appointments', 'app.py')
    
    if not os.path.exists(app_path):
        print("❌ App file not found")
        return None
    
    try:
        # Set environment for testing
        env = os.environ.copy()
        env['PORT'] = '8080'
        env['TESTING'] = 'true'
        
        # Start the app in background
        process = subprocess.Popen(
            [sys.executable, app_path],
            cwd=os.path.dirname(app_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for startup
        import time
        time.sleep(3)
        
        # Check if it's running
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                print("✅ Local app started successfully")
                return process
        except:
            process.terminate()
            print("❌ Failed to start local app")
    
    except Exception as e:
        print(f"❌ Error starting local app: {e}")
    
    return None

def main():
    """Main test runner"""
    print("🏥 Medical Appointments API Test Runner")
    print("=" * 60)
    
    # Check if app is available
    app_url = check_app_availability()
    local_process = None
    
    if not app_url:
        print("🚀 No running app found, attempting to start locally...")
        local_process = run_local_app()
        if local_process:
            app_url = "http://localhost:8080"
    
    if not app_url:
        print("❌ No app available for testing")
        print("💡 To test:")
        print("   1. Start the app locally: cd apps/medical-appointments && python app.py")
        print("   2. Or set INSTANCE_URL environment variable")
        sys.exit(1)
    
    # Set test environment
    os.environ['TEST_BASE_URL'] = app_url
    
    print(f"🧪 Running tests against: {app_url}")
    print("=" * 60)
    
    try:
        # Import and run tests
        from test_medical_appointments_api import TestMedicalAppointmentsAPI
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestMedicalAppointmentsAPI)
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\n❌ FAILURES:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\n⚠️ ERRORS:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        
        if result.wasSuccessful():
            print("\n🎉 ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n❌ {len(result.failures) + len(result.errors)} TESTS FAILED")
            return 1
    
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1
    
    finally:
        # Clean up local process if started
        if local_process:
            print("🛑 Stopping local test app...")
            local_process.terminate()
            local_process.wait()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
