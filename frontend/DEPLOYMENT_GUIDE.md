# Layered UI Deployment Guide for Stakeholders

## Overview

Grace now has 4 operational dashboards providing complete visibility:
- **Layer 1**: Operations (Health & Resources)
- **Layer 2**: Orchestration (HTM & Tasks)
- **Layer 3**: Intent (Goals & Learning)
- **Layer 4**: Development (Logs & Diagnostics)

---

## Pre-Deployment Checklist

### Backend Requirements:
- [x] All services deployed
- [x] Database migrations applied
- [x] API endpoints operational
- [ ] Environment variables configured
- [ ] CORS configured for frontend domain
- [ ] Rate limiting enabled

### Frontend Requirements:
- [x] All dashboard components built
- [ ] Backend API URLs configured
- [ ] Authentication implemented
- [ ] Build optimization completed
- [ ] Hosting provider selected

---

## Configuration

### 1. Backend API Connection

Create `frontend/.env`:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

# Production
# VITE_API_BASE_URL=https://api.grace-ai.com
# VITE_WS_URL=wss://api.grace-ai.com/ws
```

### 2. API Client Setup

Update `frontend/src/api/client.ts`:
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### 3. WebSocket for Real-Time Updates

```typescript
// frontend/src/services/websocket.ts
const ws = new WebSocket(import.meta.env.VITE_WS_URL);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  // Route to appropriate dashboard
  if (data.topic === 'htm.task.completed') {
    updateLayer2Dashboard(data.payload);
  } else if (data.topic === 'agentic.intent.completed') {
    updateLayer3Dashboard(data.payload);
  }
};
```

---

## Build & Deploy

### Development Build:
```bash
cd frontend
npm install
npm run dev
# Access: http://localhost:5173
```

### Production Build:
```bash
cd frontend
npm run build
# Output: frontend/dist/

# Serve with nginx, Vercel, Netlify, or any static host
```

### Docker Deployment:
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Stakeholder Access Roles

### Operators (Layer 1 Focus):
**Access**: Health, resources, error tracking  
**Use Cases**:
- Monitor system uptime
- Check resource utilization
- Review error logs
- Verify service health

### HTM Team (Layer 2 Focus):
**Access**: Task metrics, SLAs, throughput  
**Use Cases**:
- Monitor SLA compliance
- Optimize task routing
- Balance worker loads
- Identify bottlenecks

### Product Team (Layer 3 Focus):
**Access**: Intent tracking, outcomes, learning  
**Use Cases**:
- Track goal completion
- Review success rates
- Monitor intent→task flow
- Assess learning effectiveness

### Developers (Layer 4 Focus):
**Access**: Logs, playbooks, diagnostics  
**Use Cases**:
- Debug issues
- Review playbook executions
- Monitor self-healing
- Access raw logs

---

## Feedback Collection

### Metrics to Track:
- Dashboard load time
- API response times
- User engagement (which layers viewed most)
- Error rates
- Feature requests

### Feedback Form:
```
1. Which layer do you use most? (1/2/3/4)
2. What information is missing?
3. What's confusing or unclear?
4. Desired refresh rate? (Current: 5-20s)
5. Mobile access needed? (Yes/No)
6. Export data needed? (Yes/No)
```

---

## Iteration Plan

### Week 1: Initial Deployment
- [ ] Deploy to staging
- [ ] Give access to 5 stakeholders
- [ ] Collect initial feedback
- [ ] Fix critical issues

### Week 2: Enhancements
- [ ] Add requested features
- [ ] Improve performance
- [ ] Add data export
- [ ] Mobile optimization

### Week 3: Production
- [ ] Deploy to production
- [ ] Rollout to all stakeholders
- [ ] Monitor usage
- [ ] Continuous improvement

---

## Known Limitations

### Current:
- No authentication yet (open access)
- No real-time WebSocket (polling only)
- No data export
- No mobile optimization
- No historical charts (point-in-time only)

### Planned:
- Add OAuth authentication
- WebSocket real-time updates
- CSV/JSON export
- Mobile responsive design
- Time-series charts with Chart.js

---

## Support

### Issues:
Create GitHub issue with:
- Which layer
- What you were trying to do
- Expected vs actual behavior
- Screenshots

### Feature Requests:
Use feedback form or GitHub issues labeled `enhancement`

---

**Deployment Contact**: DevOps Team  
**Support Contact**: Engineering Team  
**Documentation**: [FULL_INTEGRATION_COMPLETE.md](file:///c:/Users/aaron/grace_2/docs/FULL_INTEGRATION_COMPLETE.md)
