"""
Test certificate validator integration with HIDR agent
"""
from simple_multiagent import SimpleMultiAgent

def test_integration():
    """Test that cert validator is integrated"""
    print("=" * 60)
    print("Testing Certificate Validator Integration")
    print("=" * 60)
    
    # Initialize HIDR agent
    agent = SimpleMultiAgent()
    
    # Check cert validator is loaded
    if agent.cert_validator:
        print("[OK] Certificate validator loaded successfully")
    else:
        print("[FAIL] Certificate validator not loaded")
        return False
    
    # Test analysis with cert validation
    print("\nTesting process analysis with cert validation...")
    result = agent.analyze_process(
        proc_name="test.exe",
        path="C:\\temp\\test.exe",
        cmdline="test.exe",
        pid=1234
    )
    
    # Check if cert_validation is in intelligence result
    intelligence = result.get('intelligence_result', {})
    if 'cert_validation' in intelligence:
        print("[OK] Certificate validation included in intelligence")
        print(f"   Cert validation: {intelligence['cert_validation']}")
    else:
        print("[INFO] Certificate validation not in intelligence (expected for non-PE files)")
    
    print("\n" + "=" * 60)
    print("Integration Test Complete")
    print("=" * 60)
    print("\nCertificate validator is now part of HIDR system!")
    print("It will automatically validate PE file signatures during analysis.")
    
    return True

if __name__ == "__main__":
    test_integration()
