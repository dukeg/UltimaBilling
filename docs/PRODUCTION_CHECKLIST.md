# Production checklist

- Replace `SECRET_KEY` with a generated secret.
- Use managed PostgreSQL and Redis.
- Run Alembic migrations instead of relying on `create_all`.
- Configure Stripe/Razorpay webhook secrets and HTTPS endpoints.
- Switch `STORAGE_BACKEND=s3` for durable PDF storage.
- Set SMTP credentials for a transactional provider.
- Put backend behind HTTPS and restrict CORS to your frontend domain.
- Add monitoring, backups, rate limits, and error tracking before customer traffic.
