# Deploy Grace to Kubernetes - PowerShell

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Deploying Grace to Kubernetes" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check kubectl
Write-Host "→ Checking kubectl..." -ForegroundColor Yellow
try {
    $kubectlVersion = kubectl version --client --short 2>$null
    Write-Host "✓ kubectl found: $kubectlVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ kubectl not found - please install Kubernetes CLI" -ForegroundColor Red
    exit 1
}

# Check cluster connection
Write-Host ""
Write-Host "→ Checking cluster connection..." -ForegroundColor Yellow
try {
    kubectl cluster-info | Out-Null
    Write-Host "✓ Connected to Kubernetes cluster" -ForegroundColor Green
} catch {
    Write-Host "✗ Cannot connect to Kubernetes cluster" -ForegroundColor Red
    Write-Host "  Make sure your cluster is running (minikube, kind, or cloud)" -ForegroundColor Yellow
    exit 1
}

# Update secret with actual values
Write-Host ""
Write-Host "⚠ IMPORTANT: Update kubernetes/grace-deployment.yaml with your secrets!" -ForegroundColor Yellow
Write-Host "  • AMP_API_KEY" -ForegroundColor White
Write-Host "  • SECRET_KEY" -ForegroundColor White
Write-Host "  • POSTGRES_PASSWORD" -ForegroundColor White
Write-Host ""
$continue = Read-Host "Continue with deployment? (y/n)"

if ($continue -ne 'y') {
    Write-Host "Deployment cancelled" -ForegroundColor Yellow
    exit 0
}

# Apply manifests
Write-Host ""
Write-Host "→ Applying Kubernetes manifests..." -ForegroundColor Yellow
kubectl apply -f kubernetes/grace-deployment.yaml

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Manifests applied successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Deployment failed" -ForegroundColor Red
    exit 1
}

# Wait for pods
Write-Host ""
Write-Host "→ Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=grace -n grace --timeout=300s

# Show status
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Deployment Status" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

kubectl get all -n grace

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Grace Deployed to Kubernetes!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To access Grace:" -ForegroundColor Cyan
Write-Host "  kubectl port-forward -n grace svc/grace-backend-service 8000:8000" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Cyan
Write-Host "  kubectl logs -n grace -l component=backend -f" -ForegroundColor White
Write-Host ""
Write-Host "To scale backend:" -ForegroundColor Cyan
Write-Host "  kubectl scale deployment grace-backend -n grace --replicas=5" -ForegroundColor White
Write-Host ""
