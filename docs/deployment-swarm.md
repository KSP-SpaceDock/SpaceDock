# Docker Swarm Deployment

SpaceDock can be deployed as a Docker Swarm stack for production with automatic failover and horizontal scaling.

## Prerequisites

- Docker Swarm cluster initialized (`docker swarm init`)
- At least 1 manager node and 2 worker nodes (3-node setup recommended)
- Traefik running as ingress router on the swarm

## Quick Start

```bash
# Build images
docker build -t spacedock_backend_prod -f Dockerfile --target backend-prod .
docker build -t spacedock_celery -f Dockerfile --target celery .
docker build -t spacedock_frontend -f frontend/Dockerfile .

# Deploy stack
docker stack deploy -c docker-compose-prod.yml spacedock --with-registry-auth
```

Or use the deployment script:

```bash
./deploy-swarm.sh
```

## Service Architecture

| Service | Replicas | Placement | Description |
|---------|----------|-----------|-------------|
| db | 1 | Manager | PostgreSQL primary database |
| db-replica | 1 | Worker | PostgreSQL replica (read scaling) |
| redis | 2 | Workers | Redis session/cache (redundant) |
| backend | 3 | All nodes | Flask app (uwsgi) |
| celery | 2 | All nodes | Background task workers |
| frontend | 2 | All nodes | Nginx frontend (ports 80/443) |
| clamav | 1 | Manager | Antivirus scanning |
| adminer | 1 | Manager | Database admin UI (port 8080) |

## Health Checks

All critical services have health checks configured:

- **PostgreSQL**: `pg_isready -U postgres` every 10s
- **Redis**: `redis-cli ping` every 10s
- **Backend**: HTTP check on port 9998 every 30s
- **Frontend**: HTTP check on port 80 every 30s

Services that fail health checks are automatically restarted up to 3 times with a 5-second delay.

## Failover Strategy

- Services spread across nodes using Docker Swarm's default placement
- Database and Redis on separate nodes from application servers
- Multiple backend/frontend replicas ensure no single point of failure
- Rolling updates deploy services one replica at a time (5-10s delay)

## Scaling

Scale services dynamically based on load:

```bash
# Scale backend
docker service scale spacedock_backend=5

# Scale Celery workers
docker service scale spacedock_celery=3

# Scale frontend
docker service scale spacedock_frontend=3
```

## Monitoring

```bash
# Stack status
docker stack ps spacedock

# Service logs
docker service logs -f spacedock_backend

# Service list
docker service ls
```

## Updates

```bash
# Build new images
docker build -t spacedock_backend_prod:latest -f Dockerfile --target backend-prod .

# Redeploy stack (rolling update)
docker stack deploy -c docker-compose-prod.yml spacedock
```

## Rollback

```bash
# Remove stack
docker stack rm spacedock

# Re-deploy previous version
docker stack deploy -c docker-compose-prod.yml spacedock
```

## Environment Variables

Required:
- `POSTGRES_PASSWORD` - Database password
- `CONNECTION_STRING` - Database connection string

Optional (defaults provided):
- See `.env.example` for all configurable options

## Network Configuration

The stack uses an overlay network (`spacedock-net`) for cross-node communication. Frontend services expose:

- Port 80: HTTP
- Port 443: HTTPS (requires SSL termination at reverse proxy)
- Port 8080: Adminer database admin
- Port 5432: PostgreSQL (internal only)

## Traefik Integration

The compose file includes Traefik labels for automatic ingress routing. Update the hostnames in the compose file:

```yaml
labels:
  - traefik.enable=true
  - traefik.http.routers.frontend.rule=Host(`your-domain.com`)
```