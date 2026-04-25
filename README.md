# Universal Billing SaaS V4

A more commercial SaaS billing platform: FastAPI backend, PostgreSQL, Redis/Celery jobs, Next.js dashboard, JWT auth, RBAC, audit logs, PDF invoice storage, Stripe/Razorpay webhook verification, recurring subscriptions, and deployment starters.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Then seed/login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/bootstrap
```

Open:

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- MailHog: http://localhost:8025

Default local admin after bootstrap:

- `admin@example.com`
- `Admin@12345`

## V4 commercial additions

- Next.js dashboard shell instead of static HTML
- Alembic migration scaffold
- Hardened Stripe and Razorpay webhook signature checks
- Idempotent payment event processing
- Local/S3 PDF storage abstraction
- Subscription lifecycle fields: trial, cancel-at-period-end, recurring generation
- Celery beat jobs for recurring invoices and overdue invoice marking
- Admin RBAC and audit logs
- Kubernetes and Render deployment starters
- Production checklist

## Important limits

This is still an MVP commercial foundation, not a fully audited fintech product. Before live money movement, complete provider-specific checkout creation, test webhooks with live provider CLIs, add automated tests, configure secrets, and complete compliance review for your target market.
