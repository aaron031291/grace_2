# Grace Kubernetes Deployment

## 🚀 Quick Deploy

```powershell
# From repository root
.\kubernetes\deploy.ps1
```

## 📋 What Gets Deployed

- **Namespace**: `grace`
- **Backend**: 3 pods (autoscaling 2-10)
- **Frontend**: 2 pods
- **PostgreSQL**: 1 pod with persistent volume
- **Redis**: 1 pod with persistent volume
- **Ingress**: SSL-enabled external access
- **HPA**: Horizontal Pod Autoscaler

## 🔧 Before Deploying

### 1. Update Secrets
Edit `grace-deployment.yaml` line ~25:
```yaml
stringData:
  amp-api-key: "YOUR_ACTUAL_AMP_API_KEY"
  secret-key: "your-secret-key-here"
  postgres-password: "your-secure-password"
```

### 2. Update Ingress Host
Edit `grace-deployment.yaml` line ~400:
```yaml
- host: grace.yourdomain.com  # Change to your domain
```

## 📊 Architecture

```
Internet
  ↓
Ingress (SSL)
  ↓
  ├─→ Frontend Service → Frontend Pods (2)
  └─→ Backend Service → Backend Pods (3-10, autoscaling)
        ↓
        ├─→ PostgreSQL (persistent)
        └─→ Redis (cache)
```

## 🎯 Commands

```bash
# Deploy
kubectl apply -f grace-deployment.yaml

# Check status
kubectl get all -n grace

# View logs
kubectl logs -n grace -l component=backend -f

# Scale manually
kubectl scale deployment grace-backend -n grace --replicas=5

# Port forward for local access
kubectl port-forward -n grace svc/grace-backend-service 8000:8000

# Delete deployment
kubectl delete namespace grace
```

## ✅ Grace in Kubernetes

Production-ready with autoscaling, health checks, and persistent storage!
