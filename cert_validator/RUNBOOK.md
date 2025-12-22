# Certificate Validator Runbook

## Quick Reference

**Service**: HIDR Certificate Validator  
**Port**: 8001  
**Health Check**: `GET /api/expert/status`  
**API Key**: `hidr-agent-key-12345` (change in production)

---

## Deployment

### Prerequisites
- Docker & Docker Compose installed
- Python 3.10+ (for local development)
- Network access for OCSP/CRL queries
- 2GB RAM minimum, 4GB recommended

### Initial Deployment

```bash
# 1. Clone repository
cd cert_validator/

# 2. Build and start services
docker-compose up -d

# 3. Verify health
curl http://localhost:8001/api/expert/status

# 4. Check logs
docker-compose logs -f cert-validator
```

### Configuration

Edit `docker-compose.yml` environment variables:
- `LOG_LEVEL`: INFO, DEBUG, WARNING, ERROR
- `CACHE_TTL`: Cache TTL in seconds (default: 86400)
- `MAX_WORKERS`: Worker threads (default: 2)

### API Key Management

**Generate new API key:**
```python
import secrets
api_key = f"hidr-agent-key-{secrets.token_urlsafe(16)}"
print(api_key)
```

Update in `cert_validator/api.py`:
```python
VALID_API_KEYS = {"your-new-key-here"}
```

---

## Canary Rollout Plan

### Phase 1: 5% Rollout (Day 1-2)
1. Deploy to 5% of hosts
2. Monitor metrics for 48 hours:
   - OCSP failure rate < 20%
   - Validation latency p95 < 2s
   - No critical errors
3. **Go/No-Go Decision**: If metrics healthy, proceed to Phase 2

### Phase 2: 25% Rollout (Day 3-4)
1. Deploy to 25% of hosts
2. Monitor for 48 hours
3. Check alert rates and false positives
4. **Go/No-Go Decision**: Proceed to Phase 3

### Phase 3: 100% Rollout (Day 5+)
1. Deploy to all hosts
2. Continue monitoring
3. Mark as production-ready

### Rollback Triggers
- OCSP failure rate > 50%
- Validation errors > 10%
- Service downtime > 5 minutes
- Critical security issue discovered

---

## Monitoring

### Key Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| `ocsp_requests_total{status="failure"}` | > 20% | Investigate OCSP responders |
| `certs_validated_total{verdict="revoked"}` | > 0 | Alert SOC immediately |
| `cert_validation_queue_size` | > 100 | Scale workers |
| `cert_cache_total{status="hit"}` | < 50% | Increase cache TTL |

### Grafana Dashboard

Import `grafana_dashboard.json` to Grafana:
```bash
curl -X POST http://grafana:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana_dashboard.json
```

### Alerts

Prometheus alerts defined in `alert_rules.yml`:
- **HighOCSPFailureRate**: OCSP failures > 20%
- **RevokedCertificateDetected**: Revoked cert found
- **CertValidatorDown**: Service unavailable

---

## Troubleshooting

### Issue: High OCSP Failure Rate

**Symptoms**: `ocsp_requests_total{status="failure"}` increasing

**Diagnosis**:
```bash
# Check OCSP responder connectivity
docker exec hidr-cert-validator curl -v http://ocsp.example.com

# Check logs
docker-compose logs cert-validator | grep OCSP
```

**Resolution**:
1. Verify network/firewall allows OCSP traffic
2. Check OCSP responder status
3. Increase timeout in `revocation.py`
4. Fallback to CRL if OCSP unavailable

### Issue: Validation Queue Backlog

**Symptoms**: `cert_validation_queue_size` > 100

**Diagnosis**:
```bash
# Check queue size
curl http://localhost:8001/api/expert/status | jq '.queue_size'

# Check worker threads
docker stats hidr-cert-validator
```

**Resolution**:
1. Increase `MAX_WORKERS` in docker-compose.yml
2. Scale horizontally (add more instances)
3. Optimize validation logic

### Issue: Cache Miss Rate High

**Symptoms**: `cert_cache_total{status="hit"}` < 50%

**Resolution**:
1. Increase `CACHE_TTL` (default: 24h)
2. Deploy Redis for distributed cache
3. Pre-warm cache with common certs

### Issue: Service Won't Start

**Diagnosis**:
```bash
docker-compose logs cert-validator
docker-compose ps
```

**Common Causes**:
- Port 8001 already in use
- Missing dependencies
- Invalid configuration

**Resolution**:
```bash
# Stop conflicting services
lsof -i :8001
kill <PID>

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Rollback Procedure

### Emergency Rollback

```bash
# 1. Stop cert validator
docker-compose stop cert-validator

# 2. Revert to previous version
git checkout <previous-commit>
docker-compose build cert-validator
docker-compose up -d cert-validator

# 3. Verify health
curl http://localhost:8001/api/expert/status

# 4. Notify team
echo "Cert validator rolled back to $(git rev-parse HEAD)" | mail -s "Rollback" team@example.com
```

### Graceful Rollback

```bash
# 1. Scale down new version
docker-compose scale cert-validator=0

# 2. Deploy old version
docker-compose -f docker-compose.old.yml up -d

# 3. Monitor for 30 minutes
watch -n 30 'curl -s http://localhost:8001/api/expert/status | jq'

# 4. Remove new version
docker-compose down
```

---

## Maintenance

### Daily Tasks
- Check Grafana dashboard for anomalies
- Review error logs
- Verify alert rules firing correctly

### Weekly Tasks
- Clean up old job records (> 7 days)
- Review cache hit rate and adjust TTL
- Update trust store certificates

### Monthly Tasks
- Security audit of API keys
- Performance review and optimization
- Update dependencies

### Cleanup Old Jobs

```bash
# Connect to container
docker exec -it hidr-cert-validator python

# Run cleanup
from cert_validator.job_queue import job_queue
job_queue.cleanup_old_jobs(max_age_hours=168)  # 7 days
```

---

## Security

### API Key Rotation

```bash
# 1. Generate new key
python -c "import secrets; print(f'hidr-agent-key-{secrets.token_urlsafe(16)}')"

# 2. Update api.py
# 3. Restart service
docker-compose restart cert-validator

# 4. Update all agents with new key
```

### Certificate Trust Store Updates

```bash
# 1. Download latest CA bundle
curl -o ca-bundle.crt https://curl.se/ca/cacert.pem

# 2. Mount in container
# Add to docker-compose.yml volumes:
#   - ./ca-bundle.crt:/app/ca-bundle.crt:ro

# 3. Restart service
docker-compose restart cert-validator
```

---

## Performance Tuning

### Optimize for High Throughput

```yaml
# docker-compose.yml
environment:
  - MAX_WORKERS=8  # Increase workers
  - CACHE_TTL=172800  # 48 hours
  - OCSP_TIMEOUT=3  # Reduce timeout
```

### Optimize for Low Latency

```yaml
environment:
  - MAX_WORKERS=2
  - CACHE_TTL=86400  # 24 hours
  - OCSP_TIMEOUT=1  # Fast timeout
```

---

## Contact & Escalation

**On-Call**: cert-validator-oncall@example.com  
**Slack**: #hidr-cert-validator  
**PagerDuty**: cert-validator service

**Escalation Path**:
1. On-call engineer (0-15 min)
2. Team lead (15-30 min)
3. Security team (30+ min)
