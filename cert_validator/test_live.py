"""
Live test script for certificate validator
Run this to verify the service is working
"""
import requests
import json
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

def generate_test_cert():
    """Generate a test certificate"""
    private_key = rsa.generate_private_key(65537, 2048, default_backend())
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "HIDR Test"),
        x509.NameAttribute(NameOID.COMMON_NAME, "test.hidr.local"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(timezone.utc)
    ).not_valid_after(
        datetime.now(timezone.utc) + timedelta(days=365)
    ).sign(private_key, hashes.SHA256(), default_backend())
    
    return cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8001/api/expert/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Cache stats: {data['cache_stats']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_validation():
    """Test validation endpoint"""
    print("\nTesting validation endpoint...")
    try:
        cert_pem = generate_test_cert()
        
        response = requests.post(
            "http://localhost:8001/api/validate",
            headers={"X-API-Key": "hidr-agent-key-12345"},
            json={
                "type": "pem",
                "cert_pem": cert_pem,
                "intermediates": [],
                "context": {"host": "test-host", "pid": 1234}
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Validation passed")
            print(f"   Verdict: {data['verdict']}")
            print(f"   Score: {data['cert_score']}/100")
            print(f"   Chain length: {len(data['chain'])}")
            return True
        else:
            print(f"❌ Validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def test_async_job():
    """Test async job endpoint"""
    print("\nTesting async job endpoint...")
    try:
        cert_pem = generate_test_cert()
        
        # Submit job
        response = requests.post(
            "http://localhost:8001/api/validate-job",
            headers={"X-API-Key": "hidr-agent-key-12345"},
            json={
                "type": "pem",
                "cert_pem": cert_pem,
                "intermediates": [],
                "context": {}
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            job_id = data['job_id']
            print(f"✅ Job submitted: {job_id}")
            
            # Check status
            import time
            time.sleep(1)
            
            status_response = requests.get(
                f"http://localhost:8001/api/validate-job/{job_id}",
                headers={"X-API-Key": "hidr-agent-key-12345"},
                timeout=5
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   Job status: {status_data['status']}")
                return True
        
        print(f"❌ Async job failed: {response.status_code}")
        return False
    except Exception as e:
        print(f"❌ Async job error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("HIDR Certificate Validator - Live Test Suite")
    print("=" * 60)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Validation", test_validation()))
    results.append(("Async Jobs", test_async_job()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Service is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check service logs.")

if __name__ == "__main__":
    main()
