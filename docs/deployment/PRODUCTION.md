# Grace Production Deployment Guide

## 🚀 Production Deployment Options

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

**Deploy:**
```bash
# Clone repository
git clone https://github.com/yourusername/grace
cd grace_rebuild

# Configure environment
cp .env.example .env
# Edit .env with production values

# Build and start
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

**Production docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://grace:${DB_PASSWORD}@db:5432/grace
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  frontend:
    build: ./grace-frontend
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_DB: grace
      POSTGRES_USER: grace
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always

volumes:
  postgres_data:
```

### Option 2: Cloud Deployment

**AWS:**
```bash
# Use ECS/Fargate
aws ecs create-cluster --cluster-name grace-production

# Or EC2
# Launch t3.medium instance
# Install Docker
# Run docker-compose
```

**Google Cloud:**
```bash
# Cloud Run
gcloud run deploy grace-backend --source .
gcloud run deploy grace-frontend --source grace-frontend
```

**Azure:**
```bash
# Container Instances
az container create --resource-group grace \
  --name grace-backend \
  --image grace-backend:latest
```

### Option 3: VPS (DigitalOcean, Linode, etc.)

```bash
# SSH into server
ssh user@your-server

# Install dependencies
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone https://github.com/yourusername/grace
cd grace_rebuild
docker-compose up -d
```

## 🔐 Production Security

### 1. Environment Variables
```bash
# .env file
SECRET_KEY=<generate-strong-key-here>
DATABASE_URL=postgresql://grace:password@db:5432/grace
ALLOWED_ORIGINS=https://yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com
```

### 2. HTTPS/SSL
```bash
# Use Nginx reverse proxy
docker run -d -p 443:443 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  nginx:latest

# Or use Caddy (auto-SSL)
# Caddyfile:
yourdomain.com {
  reverse_proxy backend:8000
}
```

### 3. Firewall Rules
```bash
# Allow only necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 4. Database Backups
```bash
# Automated backups
0 2 * * * docker exec grace-db pg_dump -U grace grace > /backups/grace-$(date +\%Y\%m\%d).sql
```

## ⚙️ Configuration

### Backend Settings
```python
# backend/config.py
class Settings:
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    reflection_interval: int = 10
    meta_loop_interval: int = 300
    max_parallel_tasks: int = 3
    sandbox_timeout: int = 10
```

### Frontend Build
```bash
cd grace-frontend
npm run build
# Serve static files with Nginx or serve
```

## 📊 Monitoring

### Health Checks
```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Metrics
```bash
# Prometheus endpoint (future)
GET /metrics

# Current: Poll Grace APIs
GET /api/health/status
GET /api/metrics/summary
```

### Logging
```bash
# Centralized logging
docker-compose logs -f --tail=100

# Or ship to external service
# Logstash, Datadog, CloudWatch, etc.
```

## 🔄 Updates & Migrations

### Zero-Downtime Updates
```bash
# Build new image
docker build -t grace-backend:v2 .

# Rolling update
docker service update --image grace-backend:v2 grace_backend
```

### Database Migrations
```bash
# Using Alembic (future)
alembic upgrade head

# Current: Manual migration scripts
python migrations/001_add_column.py
```

## 🎯 Performance Tuning

### Backend
- Use Gunicorn with multiple workers
- Enable Redis caching
- Connection pooling for DB
- Async everywhere

### Frontend
- Build with `npm run build`
- Enable gzip compression
- CDN for static assets
- Code splitting

### Database
- PostgreSQL instead of SQLite
- Indexes on frequently queried columns
- Regular VACUUM
- Connection pooling

## 🆘 Troubleshooting

### High Memory Usage
```bash
# Check container stats
docker stats

# Limit resources
docker-compose.yml:
  services:
    backend:
      deploy:
        resources:
          limits:
            memory: 2G
```

### Slow Responses
- Check health: `/api/health/status`
- Review meta-loop recommendations
- Check database query performance
- Scale workers

### Component Failures
- Self-healing will auto-restart
- Check `/api/health/status`
- Review `/api/log/entries`
- Manual restart: `/api/health/restart`

## ✅ Production Checklist

- [ ] Change default passwords
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Set up automated backups
- [ ] Configure monitoring/alerts
- [ ] Test disaster recovery
- [ ] Document runbook procedures
- [ ] Set up CI/CD pipeline
- [ ] Load test the system

## 📈 Scaling

### Horizontal Scaling
```yaml
services:
  backend:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
```

### Database Scaling
- Read replicas
- Connection pooling
- Caching layer (Redis)
- Sharding (future)

Grace is production-ready! 🚀🔒
