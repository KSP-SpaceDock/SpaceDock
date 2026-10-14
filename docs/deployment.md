# SpaceDock Deployment Guide

This document provides comprehensive guidance for deploying SpaceDock, including Docker setup, production configuration, and deployment strategies.

## Deployment Overview

SpaceDock can be deployed using various methods:
- **Docker containers** (recommended for production)
- **Traditional server setup** with uWSGI and nginx
- **Platform-as-a-Service** (PaaS) providers

## Docker Deployment

### Prerequisites

- Docker Engine
- Docker Compose
- Git

### Docker Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KSP-SpaceDock/SpaceDock.git
   cd SpaceDock
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to configure your environment.

3. **Build and start containers:**
   ```bash
   docker-compose up -d --build
   ```

### Docker Compose Configuration

The `docker-compose.yml` file defines the following services:

- **web**: Flask application server
- **db**: PostgreSQL database
- **redis**: Redis for Celery
- **celery**: Celery worker for background tasks
- **nginx**: Reverse proxy and load balancer

### Customizing Docker Configuration

Edit `docker-compose.yml` to customize:

- **Port mappings**: Change the exposed ports
- **Environment variables**: Add or modify variables in the `environment` section
- **Volumes**: Add persistent storage for uploads or logs
- **Resource limits**: Adjust CPU and memory limits

### Building Production Images

For production, build optimized Docker images:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Traditional Server Deployment

### Prerequisites

- Ubuntu 20.04 or similar Linux distribution
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis
- Nginx
- uWSGI

### Installation Steps

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-dev python3-venv nodejs npm postgresql redis-server nginx
   ```

2. **Set up PostgreSQL:**
   ```bash
   sudo -u postgres createuser spacedock
   sudo -u postgres createdb spacedock
   sudo -u postgres psql -c "ALTER USER spacedock WITH PASSWORD 'yourpassword';"
   ```

3. **Set up Redis:**
   ```bash
   sudo systemctl enable redis
   sudo systemctl start redis
   ```

4. **Set up Nginx:**
   ```bash
   sudo cp config/nginx.conf /etc/nginx/sites-available/spacedock
   sudo ln -s /etc/nginx/sites-available/spacedock /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

5. **Set up uWSGI:**
   ```bash
   sudo cp config/uwsgi.ini /etc/uwsgi/apps-available/spacedock.ini
   sudo ln -s /etc/uwsgi/apps-available/spacedock.ini /etc/uwsgi/apps-enabled/
   ```

6. **Deploy the application:**
   ```bash
   git clone https://github.com/KSP-SpaceDock/SpaceDock.git
   cd SpaceDock
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements-prod.txt
   npm install
   ./build-frontend.sh
   ```

7. **Set up systemd service:**
   ```bash
   sudo cp config/spacedock.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable spacedock
   sudo systemctl start spacedock
   ```

## Production Configuration

### Configuration Files

- **config.ini**: Main application configuration
- **alembic.ini**: Database migration configuration
- **logging.ini**: Logging configuration
- **nginx.conf**: Nginx reverse proxy configuration
- **uwsgi.ini**: uWSGI configuration

### Environment Variables

Set environment variables in `.env` or system environment:

```bash
# Example environment variables
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@localhost/spacedock
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

### Database Migrations

Run database migrations after deployment:
```bash
alembic upgrade head
```

### Static Files

Ensure static files are built and served correctly:
```bash
./build-frontend.sh
```

## Deployment Strategies

### Blue-Green Deployment

1. Deploy new version to a separate environment
2. Test the new version
3. Switch traffic to the new version
4. Roll back if issues arise

### Rolling Deployment

1. Take one or more servers out of rotation
2. Deploy the new version
3. Bring servers back into rotation
4. Repeat until all servers are updated

### Canary Deployment

1. Deploy to a subset of users
2. Monitor for issues
3. Gradually roll out to more users
4. Full rollout if successful

## Monitoring and Logging

### Logging Configuration

Edit `logging.ini` to configure logging:

```ini
[loggers]
keys=root,spacedock

[handlers]
keys=console,file

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
```

### Monitoring Tools

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **New Relic**: Application performance monitoring

## Backup and Restore

### Database Backup

```bash
pg_dump -U spacedock -d spacedock -f spacedock_backup.sql
```

### Database Restore

```bash
psql -U spacedock -d spacedock -f spacedock_backup.sql
```

### Application Backup

```bash
tar -czvf spacedock_backup.tar.gz /path/to/spacedock
```

### Application Restore

```bash
tar -xzvf spacedock_backup.tar.gz -C /path/to/
```

## Security Best Practices

### SSL/TLS

- Use Let's Encrypt for SSL certificates
- Configure HSTS headers
- Use strong cipher suites

### Database Security

- Use strong passwords
- Restrict database access
- Regularly update PostgreSQL

### Application Security

- Keep dependencies updated
- Use security headers
- Implement CSRF protection
- Regularly audit code

### User Security

- Enforce strong passwords
- Implement rate limiting
- Use two-factor authentication
- Regularly review user permissions

## Troubleshooting

### Common Issues

**Application not starting:**
- Check logs for errors
- Verify environment variables
- Ensure dependencies are installed

**Database connection issues:**
- Verify PostgreSQL is running
- Check connection string
- Ensure user has proper permissions

**Static files not loading:**
- Verify build process completed
- Check file permissions
- Ensure Nginx is configured correctly

**Celery tasks not running:**
- Verify Redis is running
- Check Celery worker logs
- Ensure tasks are properly defined

### Debugging Tips

- Enable debug mode in development
- Use Flask's debug toolbar
- Check application logs
- Enable SQL query logging
- Use Python's pdb for interactive debugging

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://www.nginx.com/resources/wiki/)
- [uWSGI Documentation](https://uwsgi-docs.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

For questions about deployment, refer to this document or consult the team.