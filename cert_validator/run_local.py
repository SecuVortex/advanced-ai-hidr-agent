"""
Run certificate validator locally without Docker
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    import uvicorn
    from cert_validator.api import app
    
    print("Starting HIDR Certificate Validator...")
    print("API: http://localhost:8001")
    print("Health: http://localhost:8001/api/expert/status")
    print("Docs: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
