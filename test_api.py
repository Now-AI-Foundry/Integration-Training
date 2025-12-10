"""
Test script for the ServiceNow Integration Training API
Run this after starting the server to verify all endpoints work correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "training-key-001"

def print_response(title, response):
    """Pretty print API responses"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))

def test_health_check():
    """Test the health check endpoint (no auth required)"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("1. Health Check (No Auth)", response)
    return response.status_code == 200

def test_root_endpoint():
    """Test the root endpoint"""
    response = requests.get(BASE_URL)
    print_response("2. Root Endpoint", response)
    return response.status_code == 200

def test_get_records_no_auth():
    """Test GET /records without authentication (should fail)"""
    response = requests.get(f"{BASE_URL}/records")
    print_response("3. GET /records WITHOUT API Key (Should Fail)", response)
    return response.status_code == 401

def test_get_records_with_auth():
    """Test GET /records with valid authentication"""
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/records", headers=headers)
    print_response("4. GET /records WITH Valid API Key", response)
    return response.status_code == 200

def test_get_record_by_id():
    """Test GET /records/{id} with authentication"""
    headers = {"X-API-Key": API_KEY}
    record_id = "REC001"
    response = requests.get(f"{BASE_URL}/records/{record_id}", headers=headers)
    print_response(f"5. GET /records/{record_id}", response)
    return response.status_code == 200

def test_get_invalid_record():
    """Test GET /records/{id} with non-existent ID"""
    headers = {"X-API-Key": API_KEY}
    record_id = "INVALID"
    response = requests.get(f"{BASE_URL}/records/{record_id}", headers=headers)
    print_response(f"6. GET /records/{record_id} (Should Return 404)", response)
    return response.status_code == 404

def test_post_record():
    """Test POST /records to create a new record"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    new_record = {
        "name": "API Test Record",
        "category": "Testing",
        "value": 9999.99,
        "owner": "Test Script",
        "description": "Record created by test script"
    }
    response = requests.post(
        f"{BASE_URL}/records",
        headers=headers,
        json=new_record
    )
    print_response("7. POST /records (Create New Record)", response)
    return response.status_code == 201

def test_post_invalid_record():
    """Test POST /records with missing required fields"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    invalid_record = {
        "name": "Incomplete Record"
        # Missing required fields: category, value, owner
    }
    response = requests.post(
        f"{BASE_URL}/records",
        headers=headers,
        json=invalid_record
    )
    print_response("8. POST /records with Missing Fields (Should Fail)", response)
    return response.status_code == 422

def test_invalid_api_key():
    """Test with an invalid API key"""
    headers = {"X-API-Key": "invalid-key-xyz"}
    response = requests.get(f"{BASE_URL}/records", headers=headers)
    print_response("9. GET /records with Invalid API Key (Should Fail)", response)
    return response.status_code == 401

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("ServiceNow Integration Training API - Test Suite")
    print("="*60)
    print("\nMake sure the API server is running on http://localhost:8000")
    print("Start the server with: python main.py\n")

    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("GET without Auth", test_get_records_no_auth),
        ("GET with Auth", test_get_records_with_auth),
        ("GET by ID", test_get_record_by_id),
        ("GET Invalid ID", test_get_invalid_record),
        ("POST New Record", test_post_record),
        ("POST Invalid Data", test_post_invalid_record),
        ("Invalid API Key", test_invalid_api_key),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed! The API is ready for ServiceNow integration training.")
    else:
        print("\n⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    run_all_tests()
