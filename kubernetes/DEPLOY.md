# 🚀 Grace Kubernetes Deployment Guide

## ⚡ Quick Deploy - Copy & Paste

### Single Command Deploy:
```powershell
cd C:\Users\aaron\grace_2\kubernetes
kubectl apply -f grace-complete-deployment.yaml
```

That's it! This deploys:
- ✅ Grace namespace
- ✅ Backend (2 replicas, auto-scaling)
- ✅ Frontend (2 replicas)
- ✅ Services (LoadBalancer)
- ✅ Persistent volumes
- ✅ All 9 kernels + 311 APIs

---

## 📋 Step-by-Step (If You Need More Control)

### 1. Build Docker Images
```powershell
cd C:\Users\aaron\grace_2

# Build backend
docker build -t grace-backend:latest -f Dockerfile .

# Build frontend
docker build -t grace-frontend:latest -f frontend/Dockerfile ./frontend
```

### 2. Deploy to Kubernetes
```powershell
cd kubernetes
kubectl apply -f grace-complete-deployment.yaml
```

### 3. Wait for Pods to Start
```powershell
kubectl get pods -n grace --watch
```

Press Ctrl+C when all pods show `Running`

---

## 🔍 Check Status

### View Pods:
```powershell
kubectl get pods -n grace
```

### View Services:
```powershell
kubectl get services -n grace
```

### View Logs:
```powershell
# Backend logs
kubectl logs -n grace -l app=grace-backend --tail=100 -f

# Frontend logs
kubectl logs -n grace -l app=grace-frontend --tail=100 -f
```

### Get Service URLs:
```powershell
kubectl get services -n grace
```

Look for `EXTERNAL-IP` column.

---

## 🌐 Access Grace

### Get Backend URL:
```powershell
kubectl get service grace-backend-service -n grace
```

### Get Frontend URL:
```powershell
kubectl get service grace-frontend-service -n grace
```

### Test Backend:
```powershell
# Replace <EXTERNAL-IP> with actual IP from above
curl http://<EXTERNAL-IP>:8000/health
```

### Test Kernel:
```powershell
curl -X POST http://<EXTERNAL-IP>:8000/kernel/memory `
  -H "Content-Type: application/json" `
  -d '{"intent": "What do you know?"}'
```

---

## 📊 What Gets Deployed

### Backend (grace-backend)
- **Replicas:** 2 (auto-scales 2-10)
- **Resources:** 2Gi RAM, 1 CPU (up to 4Gi/2 CPU)
- **Health Checks:** /health endpoint
- **Volumes:** databases, logs, ml_artifacts
- **Port:** 8000

### Frontend (grace-frontend)
- **Replicas:** 2
- **Resources:** 512Mi RAM, 250m CPU
- **Port:** 5173

### Persistent Storage
- **Databases:** 10Gi
- **Logs:** 5Gi
- **ML Artifacts:** 20Gi

### Features Enabled
- ✅ All 9 Domain Kernels
- ✅ Self-Healing (execute mode)
- ✅ Coding Agent
- ✅ Agentic Spine
- ✅ Autonomous Improver
- ✅ Meta Loop
- ✅ Learning Aggregation

---

## 🔧 Common Commands

### Scale Backend:
```powershell
kubectl scale deployment grace-backend -n grace --replicas=5
```

### Restart Backend:
```powershell
kubectl rollout restart deployment grace-backend -n grace
```

### Update Backend Image:
```powershell
kubectl set image deployment/grace-backend grace-backend=grace-backend:v2 -n grace
```

### Port Forward (Local Access):
```powershell
# Access backend locally on localhost:8000
kubectl port-forward -n grace service/grace-backend-service 8000:8000

# Access frontend locally on localhost:5173
kubectl port-forward -n grace service/grace-frontend-service 5173:5173
```

---

## 🛑 Stop/Delete Deployment

### Delete Everything:
```powershell
kubectl delete namespace grace
```

### Delete Just Deployments:
```powershell
kubectl delete deployment grace-backend grace-frontend -n grace
```

### Keep Data, Delete Apps:
```powershell
kubectl delete deployment,service -n grace --all
# PVCs remain for data persistence
```

---

## 🔍 Troubleshooting

### Pods Not Starting?
```powershell
# Check pod status
kubectl describe pod <pod-name> -n grace

# Check events
kubectl get events -n grace --sort-by='.lastTimestamp'
```

### Image Pull Errors?
```powershell
# If using local images, load them into cluster
# For minikube:
minikube image load grace-backend:latest
minikube image load grace-frontend:latest

# For kind:
kind load docker-image grace-backend:latest
kind load docker-image grace-frontend:latest
```

### Can't Access Service?
```powershell
# Check service endpoints
kubectl get endpoints -n grace

# Use port-forward for local access
kubectl port-forward -n grace service/grace-backend-service 8000:8000
```

### Check Logs:
```powershell
# All backend logs
kubectl logs -n grace -l app=grace-backend --all-containers=true

# Specific pod
kubectl logs -n grace <pod-name>
```

---

## 🎯 Production Configuration

### For Production, Update:

1. **Resource Limits** (in deployment yaml):
   ```yaml
   resources:
     requests:
       memory: "4Gi"
       cpu: "2000m"
     limits:
       memory: "8Gi"
       cpu: "4000m"
   ```

2. **Replicas** (for high availability):
   ```yaml
   replicas: 5  # Or more
   ```

3. **Storage** (for production data):
   ```yaml
   storage: 100Gi  # Increase as needed
   ```

4. **Use Secrets** for API keys:
   ```powershell
   kubectl create secret generic grace-secrets -n grace \
     --from-literal=AMP_API_KEY=your_key_here
   ```

---

## 📈 Monitoring

### View Resource Usage:
```powershell
kubectl top pods -n grace
kubectl top nodes
```

### View Auto-Scaling Status:
```powershell
kubectl get hpa -n grace
```

### Watch Deployment:
```powershell
kubectl get deployment grace-backend -n grace --watch
```

---

**That's it! Grace is running on Kubernetes!** 🎉
