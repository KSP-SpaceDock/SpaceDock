#!/bin/bash
set -e

# SpaceDock Docker Swarm Deployment (3-Node Setup)
# Recommended: 1 manager + 2 workers
#
# Prerequisites:
#   - Docker Swarm initialized (docker swarm init)
#   - 2 worker nodes joined (docker swarm join)
#   - Traefik running as ingress router on the swarm
#
# Usage: ./deploy-swarm.sh

STACK_NAME="spacedock"
COMPOSE_FILE="docker-compose-prod.yml"

echo "=== SpaceDock Swarm Deployment ==="
echo ""

# Check if swarm is initialized
if ! docker info 2>/dev/null | grep -q "Swarm:"; then
    echo "ERROR: Docker Swarm not initialized."
    echo "Run: docker swarm init"
    exit 1
fi

echo "Building images..."
docker build -t spacedock_backend_prod -f Dockerfile --target backend-prod .
docker build -t spacedock_celery -f Dockerfile --target celery .
docker build -t spacedock_frontend -f frontend/Dockerfile .

echo ""
echo "Deploying stack: $STACK_NAME"
echo ""

# Deploy stack
docker stack deploy -c "$COMPOSE_FILE" "$STACK_NAME" --with-registry-auth

echo ""
echo "Deployment complete!"
echo ""
echo "Services deployed:"
echo "  - db (1 replica) - PostgreSQL on manager node"
echo "  - db-replica (1 replica) - PostgreSQL replica on worker"
echo "  - redis (2 replicas) - Redis on worker nodes"
echo "  - backend (3 replicas) - Flask app spread across nodes"
echo "  - celery (2 replicas) - Background workers"
echo "  - frontend (2 replicas) - Web frontend on port 80/443"
echo "  - clamav (1 replica) - Antivirus scanning"
echo "  - adminer (1 replica) - DB admin UI on port 8080"
echo ""
echo "Monitoring:"
echo "  Status:  docker stack ps $STACK_NAME"
echo "  Services: docker service ls"
echo "  Logs:    docker service logs -f $STACK_NAME_backend"
echo ""
echo "Scaling:"
echo "  Backend:  docker service scale $STACK_NAME_backend=5"
echo "  Workers:  docker service scale $STACK_NAME_celery=3"
echo "  Frontend: docker service scale $STACK_NAME_frontend=3"
echo ""
echo "Updating:"
echo "  Build new images, then: docker stack deploy -c $COMPOSE_FILE $STACK_NAME"
echo ""
echo "Rollback:"
echo "  docker stack rm $STACK_NAME"
echo ""
echo "Access:"
echo "  Frontend: http://<swarm-ip> (port 80) or https://<swarm-ip> (port 443)"
echo "  Adminer:  http://<swarm-ip>:8080"
echo ""
echo "Note: Update traefik labels in compose file with your actual domains"
echo "      (currently: spacedock.example.com and www.spacedock.example.com)"