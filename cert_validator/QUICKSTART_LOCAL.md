# Quick Start - Local Development (No Docker)

## Prerequisites

```bash
pip install cryptography fastapi uvicorn httpx pydantic
```

## Run Locally

```bash
# From project root
python cert_validator/run_local.py
```

The service will start on http://localhost:8001

## Test Endpoints

### Health Check
```bash
curl http://localhost:8001/api/expert/status
```

### API Documentation
Open browser: http://localhost:8001/docs

### Test Validation
```bash
curl -X POST http://localhost:8001/api/validate ^
  -H "X-API-Key: hidr-agent-key-12345" ^
  -H "Content-Type: application/json" ^
  -d "{\"type\":\"pem\",\"cert_pem\":\"test\",\"intermediates\":[],\"context\":{}}"
```

## Run Tests

```bash
python -m pytest cert_validator/tests/ -v
```

## Integration with HIDR Agent

Add to your agent code:

```python
from cert_validator.agent_integration import CertValidatorClient

# Initialize client
client = CertValidatorClient(
    api_url="http://localhost:8001",
    api_key="hidr-agent-key-12345"
)

# Enrich alert with cert validation
enriched_alert = client.enrich_alert(alert, cert_pem=cert_data)
```

## Troubleshooting

**Port already in use:**
```bash
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

**Import errors:**
```bash
pip install -r requirements.txt
```

**API key invalid:**
Update `cert_validator/api.py` line 28 with your key.
