# 🚀 Grace Deployment Guide

## Deployment Options

Grace can be deployed in **3 ways**:

1. **Local Development** - Direct Python execution
2. **Docker Compose** - Containerized local deployment
3. **Kubernetes** - Production-grade cloud deployment

---

## 1️⃣ Local Development (Simplest)

### PowerShell (Recommended)
```powershell
# Complete E2E boot
.\boot_grace_complete.ps1

# Or simple start
.\start_grace.ps1
```

### Features
- ✅ Full control and monitoring
- ✅ Easy debugging
- ✅ Hot reload enabled
- ✅ All logs accessible

### Requirements
- Python 3.13+
- Virtual environment (`.venv`)
- Node.js 18+ (for frontend)

---

## 2️⃣ Docker Compose (Recommended for Production)

### Quick Start
```powershell
# Build images
.\docker-build.ps1

# Start all services
.\docker-start.ps1

# Or manually
docker-compose up -d
```

### What Gets Deployed
- ✅ Grace Backend (3 replicas)
- ✅ Grace Frontend
- ✅ PostgreSQL Database
- ✅ Redis Cache
- ✅ Nginx Reverse Proxy

### Access
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Proxy: http://localhost:80

### Management
```bash
# View logs
docker-compose logs -f grace-backend

# Restart service
docker-compose restart grace-backend

# Scale backend
docker-compose up -d --scale grace-backend=5

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 3️⃣ Kubernetes (Production Cloud)

### Quick Deploy
```powershell
# Deploy to cluster
.\kubernetes\deploy.ps1

# Or manually
kubectl apply -f kubernetes/grace-deployment.yaml
```

### What Gets Deployed
- ✅ Grace Backend (3 pods, autoscaling 2-10)
- ✅ Grace Frontend (2 pods)
- ✅ PostgreSQL (1 pod, persistent storage)
- ✅ Redis (1 pod, persistent storage)
- ✅ Ingress with SSL
- ✅ Persistent volumes
- ✅ Horizontal Pod Autoscaler

### Requirements
- Kubernetes cluster (minikube, kind, GKE, EKS, AKS)
- kubectl CLI
- Ingress controller (nginx)
- cert-manager (for SSL)

### Before Deploying
1. Update `kubernetes/grace-deployment.yaml` with your secrets:
   - `amp-api-key`
   - `secret-key`
   - `postgres-password`

2. Update ingress host:
   - `grace.yourdomain.com` → your actual domain

### Management
```bash
# Check status
kubectl get all -n grace

# View logs
kubectl logs -n grace -l component=backend -f

# Scale backend
kubectl scale deployment grace-backend -n grace --replicas=5

# Port forward for local access
kubectl port-forward -n grace svc/grace-backend-service 8000:8000

# Update deployment
kubectl apply -f kubernetes/grace-deployment.yaml

# Delete everything
kubectl delete namespace grace
```

### Autoscaling
Grace backend auto-scales based on:
- CPU usage > 70%
- Memory usage > 80%
- Min replicas: 2
- Max replicas: 10

---

## 📊 Resource Requirements

### Minimum (Development)
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 10 GB

### Recommended (Production)
- **CPU**: 4-8 cores
- **RAM**: 8-16 GB
- **Storage**: 50 GB SSD

### Kubernetes Production
- **Backend pods**: 3-10 (autoscaling)
- **Per pod**: 500m CPU, 512Mi RAM (min)
- **Database**: 1 pod, 1Gi RAM, 10Gi storage
- **Total cluster**: 4+ nodes, 16+ GB RAM

---

## 🔐 Environment Variables

### Required
```bash
AMP_API_KEY=your_amp_api_key_here
SECRET_KEY=your_secret_key_here
```

### Optional
```bash
DATABASE_URL=postgresql://...  # Use PostgreSQL instead of SQLite
REDIS_URL=redis://localhost:6379
POSTGRES_PASSWORD=secure_password
LOG_LEVEL=INFO
```

---

## 🚀 Deployment Commands

### Local Development
```powershell
# Full E2E boot
.\boot_grace_complete.ps1

# Simple start
.\start_grace.ps1

# With monitoring
.\START_GRACE_AND_MONITOR.bat
```

### Docker Compose
```powershell
# Build
.\docker-build.ps1

# Start
.\docker-start.ps1

# Or manually
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Kubernetes
```powershell
# Deploy
.\kubernetes\deploy.ps1

# Or manually
kubectl create namespace grace
kubectl apply -f kubernetes/grace-deployment.yaml

# Check status
kubectl get pods -n grace

# Access
kubectl port-forward -n grace svc/grace-backend-service 8000:8000
```

---

## 📁 Deployment Files

| File | Purpose |
|------|---------|
| `boot_grace_complete.ps1` | **E2E PowerShell boot** |
| `start_grace.ps1` | Simple PowerShell start |
| `Dockerfile` | Grace backend image |
| `docker-compose.yml` | Complete Docker setup |
| `docker-build.ps1` | Build Docker images |
| `docker-start.ps1` | Start Docker services |
| `kubernetes/grace-deployment.yaml` | K8s manifests |
| `kubernetes/deploy.ps1` | K8s deployment script |

---

## 🎯 Quick Start by Environment

### Local Development
```powershell
.\boot_grace_complete.ps1
```

### Docker (Single Machine)
```powershell
.\docker-build.ps1
.\docker-start.ps1
```

### Kubernetes (Production)
```powershell
# Update secrets in kubernetes/grace-deployment.yaml
.\kubernetes\deploy.ps1
```

---

## 🔍 Health Checks

### Local
```bash
curl http://localhost:8000/health
```

### Docker
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Kubernetes
```bash
kubectl get pods -n grace
kubectl port-forward -n grace svc/grace-backend-service 8000:8000
curl http://localhost:8000/health
```

---

## 🎉 All Deployment Methods Ready!

Grace can now run on:
- ✅ **Local machine** (PowerShell E2E boot)
- ✅ **Docker** (containerized)
- ✅ **Kubernetes** (production cloud)

**Start with**: `.\boot_grace_complete.ps1` for full E2E experience! 🚀
