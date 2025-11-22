# Grace Docker Containerization

This document provides comprehensive instructions for containerizing and deploying the Grace AI system using Docker and Docker Compose.

## 🏗️ Architecture Overview

The Grace system is containerized as a multi-service application with the following components:

- **Backend API** (Python/FastAPI) - Main application server
- **Frontend UI** (Node.js/React) - Web interface
- **PostgreSQL** - Primary database (production)
- **Redis** - Caching and session storage
- **Nginx** - Reverse proxy and load balancer
- **Prometheus/Grafana** - Monitoring and observability
- **Loki/Promtail** - Log aggregation

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 20GB free disk space
- Git

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd grace
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env.docker

# Edit with your configuration
nano .env.docker
```

**Required environment variables:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `GITHUB_TOKEN` - GitHub access token (optional)
- `SECRET_KEY` - Random secret key for JWT
- `POSTGRES_PASSWORD` - Database password (production)

### 3. Deploy Locally

```bash
# Make scripts executable (Windows: skip this step)
chmod +x scripts/docker/*.sh

# Deploy all services
./scripts/docker/deploy.sh start

# Or use Docker Compose directly
docker-compose --env-file .env.docker up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🛠️ Development Workflow

### Building Images

```bash
# Build all images locally
./scripts/docker/build.sh all

# Build specific service
./scripts/docker/build.sh backend

# Build with custom version
./scripts/docker/build.sh -v v1.2.3 all
```

### Publishing to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push images
./scripts/docker/push.sh -v v1.2.3 all

# Create multi-arch manifests
./scripts/docker/push.sh manifest
```

### Deployment Management

```bash
# Start services
./scripts/docker/deploy.sh start

# Stop services
./scripts/docker/deploy.sh stop

# Restart services
./scripts/docker/deploy.sh restart

# View status
./scripts/docker/deploy.sh status

# View logs
./scripts/docker/deploy.sh logs
./scripts/docker/deploy.sh logs backend
./scripts/docker/deploy.sh logs-follow
```

## 🏭 Production Deployment

### 1. Production Configuration

```bash
# Copy production environment
cp .env.docker .env.prod

# Edit production settings
nano .env.prod
```

### 2. Deploy to Production

```bash
# Use production compose file
./scripts/docker/deploy.sh -f docker-compose.prod.yml start

# Or with Docker Compose
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 3. SSL/TLS Setup (Recommended)

For production, configure SSL certificates in `nginx/ssl/` and update `nginx/nginx.conf`.

### 4. Scaling Services

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale with production config
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## 📊 Monitoring & Observability

### Accessing Monitoring Stack

- **Grafana**: http://localhost:3000
  - Default credentials: admin/admin
  - Grace dashboards are pre-configured

- **Prometheus**: http://localhost:9090
  - Metrics collection and alerting

- **Loki**: Log aggregation and querying

### Health Checks

```bash
# Check all service health
./scripts/docker/deploy.sh health

# Manual health check
curl http://localhost:8000/health
curl http://localhost:5173
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GRACE_PORT` | Backend API port | 8000 | No |
| `FRONTEND_PORT` | Frontend UI port | 5173 | No |
| `DATABASE_URL` | Database connection URL | SQLite | No |
| `REDIS_URL` | Redis connection URL | redis://redis:6379 | No |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `GITHUB_TOKEN` | GitHub access token | - | No |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `LOG_LEVEL` | Logging level | INFO | No |

### Docker Compose Files

- `docker-compose.yml` - Development configuration
- `docker-compose.prod.yml` - Production configuration
- `monitoring/docker-compose.yml` - Monitoring stack only

### Volumes

- `grace_db_data` - Database files
- `grace_storage` - File storage
- `grace_logs` - Application logs
- `grace_ml_artifacts` - ML model artifacts
- `redis_data` - Redis persistence
- `prometheus_data` - Metrics data
- `grafana_data` - Dashboard configurations

## 🔍 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check logs
./scripts/docker/deploy.sh logs

# Check Docker system
docker system df
docker system prune
```

#### Port Conflicts
```bash
# Find processes using ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173

# Change ports in .env.docker
GRACE_PORT=8001
FRONTEND_PORT=5174
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
./scripts/docker/deploy.sh logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Memory Issues
```bash
# Check resource usage
docker stats

# Increase Docker memory limit in Docker Desktop
# Or reduce service resource limits in compose files
```

### Debug Mode

```bash
# Run with debug logging
GRACE_ENV=development ./scripts/docker/deploy.sh start

# Access container shell
docker exec -it grace-backend bash

# Check environment variables
docker exec grace-backend env
```

## 🔒 Security Considerations

### Production Security

1. **Change default passwords** in `.env.prod`
2. **Use strong SECRET_KEY** for JWT tokens
3. **Enable SSL/TLS** with valid certificates
4. **Configure firewall** rules
5. **Regular security updates** of base images
6. **Monitor logs** for suspicious activity

### Container Security

- Non-root user execution
- Read-only root filesystem where possible
- Security options: `no-new-privileges`
- Resource limits and reservations
- Minimal base images (Alpine Linux)

## 📈 Performance Optimization

### Resource Allocation

```yaml
# In docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '0.5'
      memory: 1G
```

### Database Optimization

- Use PostgreSQL in production
- Configure connection pooling
- Set appropriate memory limits
- Regular vacuum and analyze operations

### Caching Strategy

- Redis for session storage
- Application-level caching
- CDN for static assets (future)

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Grace
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker images
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          ./scripts/docker/build.sh -v ${{ github.sha }} multiplatform
          ./scripts/docker/push.sh -v ${{ github.sha }} all

      - name: Deploy to production
        run: |
          ssh user@server << EOF
            cd /opt/grace
            git pull
            ./scripts/docker/deploy.sh -f docker-compose.prod.yml restart
          EOF
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Grace System Documentation](./README.md)

## 🤝 Contributing

When contributing to the containerization:

1. Update this documentation
2. Test changes in development environment
3. Ensure production configurations are updated
4. Follow security best practices
5. Update CI/CD pipelines if needed

## 📞 Support

For issues related to containerization:

1. Check this documentation
2. Review logs: `./scripts/docker/deploy.sh logs`
3. Check GitHub issues
4. Create new issue with:
   - Docker version: `docker --version`
   - Docker Compose version: `docker-compose --version`
   - Environment: `cat .env.docker` (redact secrets)
   - Error logs and full command output