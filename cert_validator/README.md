# HIDR Certificate Validator Subsystem

Production-ready CA certificate validation service with OCSP, CRL, and CT checking.

## Quick Start

```bash
# Start services
cd cert_validator/
docker-compose up -d

# Verify health
curl http://localhost:8001/api/expert/status

# Test validation
curl -X POST http://localhost:8001/api/validate \
  -H "X-API-Key: hidr-agent-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"type":"pem","cert_pem":"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"}'
```

## Architecture

- **Core Validator**: Certificate parsing, chain building, policy checks
- **Revocation Checker**: OCSP and CRL validation with caching
- **CT Checker**: Certificate Transparency log verification
- **REST API**: FastAPI with JWT authentication
- **Job Queue**: Async validation with threading
- **Metrics**: Prometheus-compatible metrics

## Test Results

**41/41 tests passing** (100% success rate)

- Core validation: 6 tests
- Revocation (OCSP/CRL): 5 tests
- CT & TLS: 7 tests
- Job queue & cache: 9 tests
- REST API: 7 tests
- Agent integration: 7 tests

## Deployment

See [RUNBOOK.md](RUNBOOK.md) for complete deployment guide.

## API Endpoints

- `POST /api/validate` - Sync validation (1-2s)
- `POST /api/validate-job` - Async validation (full check)
- `GET /api/validate-job/{job_id}` - Job status
- `GET /api/expert/status` - Health check

## Monitoring

- Grafana dashboard: `grafana_dashboard.json`
- Prometheus alerts: `alert_rules.yml`
- Metrics endpoint: `/metrics`

## Security

- API key authentication required
- Rate limiting per agent IP
- Input validation and sanitization
- Non-root container user

## Performance

- Sync validation: <2s (cached)
- Async validation: 5-10s (full OCSP/CRL/CT)
- Cache hit rate: >80% typical
- Throughput: 100+ validations/sec

## License

MIT License - Part of HIDR v3.0
