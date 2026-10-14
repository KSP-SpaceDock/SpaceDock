# SpaceDock Deployment Guidelines

This document provides comprehensive deployment-specific guidelines for SpaceDock, including environment configurations, deployment strategies, monitoring, backups, and rollback procedures.

## Environment-Specific Configurations

### Development Environment

**Configuration File:** `config.ini.dev`

**Key Settings:**
- Debug mode enabled
- Database: SQLite for simplicity
- Logging level: DEBUG
- Rate limiting: Disabled or relaxed
- Email: Console-based or local SMTP

**Example Configuration:**
```ini
[DEFAULT]
debug = True

[DATABASE]
driver = sqlite
database = spacedock-dev.db

[LOGGING]
level = DEBUG

[RATE_LIMITING]
enabled = False
```

### Staging Environment

**Configuration File:** `config.ini.staging`

**Key Settings:**
- Debug mode disabled
- Database: PostgreSQL
- Logging level: INFO
- Rate limiting: Enabled but relaxed
- Email: Test SMTP server

**Example Configuration:**
```ini
[DEFAULT]
debug = False

[DATABASE]
driver = postgresql
database = spacedock-staging
user = spacedock
password = staging-password
host = localhost
port = 5432

[LOGGING]
level = INFO

[RATE_LIMITING]
enabled = True
limit = 120 per minute
```

### Production Environment

**Configuration File:** `config.ini.prod`

**Key Settings:**
- Debug mode disabled
- Database: PostgreSQL with replication
- Logging level: INFO (DEBUG for specific modules if needed)
- Rate limiting: Enabled
- Email: Production SMTP server
- Security headers: Enabled

**Example Configuration:**
```ini
[DEFAULT]
debug = False

[DATABASE]
driver = postgresql
database = spacedock
user = spacedock
password = production-password
host = db-primary
port = 5432

[LOGGING]
level = INFO

[RATE_LIMITING]
enabled = True
limit = 60 per minute

[SECURITY]
hsts = True
csp = True
```

## Zero-Downtime Deployment Strategies

### Blue-Green Deployment

**Steps:**
1. Deploy the new version to a separate environment (e.g., `green`) alongside the current version (`blue`).
2. Run smoke tests on the new environment to ensure stability.
3. Update the load balancer to route traffic to the new environment.
4. Monitor the new environment for issues.
5. If issues arise, roll back by switching the load balancer back to the old environment.
6. Once confirmed stable, decommission the old environment.

**Tools:**
- Load balancer (e.g., Nginx, HAProxy)
- Smoke test scripts
- Monitoring tools (e.g., Prometheus, Grafana)

### Rolling Deployment

**Steps:**
1. Take one or more servers out of rotation.
2. Deploy the new version to the servers.
3. Bring the servers back into rotation.
4. Repeat for the remaining servers.
5. Monitor for issues during the deployment.

**Tools:**
- Deployment automation (e.g., Ansible, Fabric)
- Monitoring tools
- Health checks

### Canary Deployment

**Steps:**
1. Deploy the new version to a subset of users (e.g., 5%).
2. Monitor for issues.
3. Gradually increase the percentage of users on the new version.
4. If issues arise, roll back by redirecting users to the old version.
5. Once fully deployed, monitor for any lingering issues.

**Tools:**
- Feature flags
- A/B testing tools
- Monitoring tools

## Monitoring and Logging Setup

### Monitoring Tools

**Recommended Tools:**
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization of metrics
- **Sentry**: Error tracking
- **New Relic**: Application performance monitoring

**Key Metrics to Monitor:**
- Application health (response times, error rates)
- Database performance (query times, connections)
- API usage (request rates, response times)
- Background jobs (Celery task queue length, processing times)
- System resources (CPU, memory, disk usage)

### Logging Configuration

**Logging Levels:**
- **DEBUG**: Detailed information for debugging (development only)
- **INFO**: General information about application operation
- **WARNING**: Indication of potential issues
- **ERROR**: Serious problems that may require attention
- **CRITICAL**: Critical issues that may cause the application to fail

**Example Logging Configuration (`logging.ini`):**
```ini
[loggers]
keys=root,spacedock

[handlers]
keys=console,file,syslog

[formatters]
keys=generic

[logger_spacedock]
handlers=console,file
level=INFO
propagate=0

[handler_console]
class=StreamHandler
formatter=generic
args=(sys.stdout,)

[handler_file]
class=FileHandler
formatter=generic
args=('logs/spacedock.log',)

[handler_syslog]
class=SysLogHandler
formatter=generic
args=('/dev/log',)

[formatter_generic]
format=%(asctime)s %(levelname)s %(name)s %(message)s
```

### Alerting

**Alerting Rules:**
- Application downtime
- High error rates
- Slow response times
- Database connection issues
- Background job failures
- High system resource usage

**Example Alerting Configuration (Prometheus):**
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High error rate on {{ $labels.instance }}"
    description: "{{ $value }}% of requests are failing"
```

## Backup and Restore Procedures

### Database Backup

**Frequency:** Daily automated backups, with weekly and monthly retention.

**Backup Command:**
```bash
pg_dump -U spacedock -d spacedock -Fc -f spacedock_backup_$(date +%Y%m%d).dump
```

**Backup Retention:**
- Daily backups: Retain for 7 days
- Weekly backups: Retain for 4 weeks
- Monthly backups: Retain for 12 months

### Application Backup

**Frequency:** Daily automated backups.

**Backup Command:**
```bash
tar -czvf spacedock_backup_$(date +%Y%m%d).tar.gz /path/to/spacedock
```

**Backup Location:**
- Remote storage (e.g., S3, Backblaze)
- Offsite storage for disaster recovery

### Restore Procedures

#### Database Restore

**Steps:**
1. Stop the application to prevent data changes during restore.
2. Restore the database from backup:
   ```bash
   pg_restore -U spacedock -d spacedock -C spacedock_backup_YYYYMMDD.dump
   ```
3. Verify the database restore:
   ```bash
   psql -U spacedock -d spacedock -c "SELECT COUNT(*) FROM mods;"
   ```
4. Start the application.

#### Application Restore

**Steps:**
1. Stop the application.
2. Restore the application files from backup:
   ```bash
   tar -xzvf spacedock_backup_YYYYMMDD.tar.gz -C /path/to/
   ```
3. Verify the application files:
   ```bash
   ls -l /path/to/spacedock
   ```
4. Start the application.

## Rollback Procedures

### Application Rollback

**Steps:**
1. Identify the issue causing the need for rollback.
2. Stop the application.
3. Deploy the previous version of the application.
4. Start the application.
5. Monitor for issues.
6. If the rollback is successful, investigate the issue and fix it.

**Tools:**
- Deployment automation (e.g., Ansible, Fabric)
- Version control (e.g., Git)
- Monitoring tools

### Database Rollback

**Steps:**
1. Identify the issue causing the need for rollback.
2. Restore the database from the most recent backup.
3. Verify the database restore.
4. Monitor for issues.
5. If the rollback is successful, investigate the issue and fix it.

**Tools:**
- Database backups
- Monitoring tools

### Rollback Checklist

1. **Pre-R