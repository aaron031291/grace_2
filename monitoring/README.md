# Grace Monitoring Setup  
  
This directory contains monitoring configuration for the Grace system.  
  
## Components  
  
- **Prometheus**: Metrics collection and storage  
- **Grafana**: Dashboard and visualization  
- **Grace Dashboard**: Pre-configured dashboard for Grace metrics  
  
## Setup  
  
1. Start the monitoring stack:  
   ```bash  
   docker-compose up -d  
   ```  
  
2. Access Grafana at http://localhost:3000 (admin/admin)  
  
3. Access Prometheus at http://localhost:9090  
  
## Grace Metrics  
  
The Grace system exposes metrics at `/metrics` endpoint including:  
  
- Action execution metrics  
- Contract verification metrics  
- Rollback and approval metrics  
- Mission and job tracking  
- Benchmark performance  
  
## Health Checks  
  
- `/api/health`: Comprehensive health check  
- `/api/health/live`: Liveness probe  
- `/api/health/ready`: Readiness probe 
