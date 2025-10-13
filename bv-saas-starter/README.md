# Business Valuation SaaS — Starter Repo

This is a minimal scaffold to deploy a FastAPI + Next.js app to **GCP Cloud Run** with **Terraform** and **Cloud Build**.
It includes:
- API (FastAPI) with `/healthz` and a basic uploads flow
- Web (Next.js) upload page
- Terraform (dev env) to enable core services/buckets/SQL (simplified)
- Cloud Build configs to build/deploy API and workers (template)

> Replace placeholder values and expand modules as needed. See your canvas "Kickstart Pack" for the full, production-ready version.
