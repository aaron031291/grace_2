# Cost Baseline

| Component | Suggested SKU | Est. Monthly (USD) | Notes |
| --- | --- | --- | --- |
| Backend API | 1× t3.small (AWS) | 30 | Fits FastAPI + background workers |
| Database | RDS PostgreSQL db.t3.micro | 15 | Enable automated backups |
| Frontend | S3/CloudFront | 5 | Or host via Vercel/Netlify free tier |
| Monitoring | Grafana Cloud Free / Loki | 0 | Upgrade when logs > 10GB/mo |

Assumptions:
- Moderate usage (internal team).
- Burst workloads handled via manual scaling.

Next steps for AMP:
- Capture real usage via CloudWatch/Prometheus once deployed.
- Model SaaS tiers (multi-tenant) to forecast scaling costs.
- Automate standby environment shutdown when idle.
