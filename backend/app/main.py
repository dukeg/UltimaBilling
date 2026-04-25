from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import Base, engine
from .routers import auth, customers, invoices, payments, analytics, subscriptions, admin

# Local convenience. Production should run Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="4.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
for router in [auth.router, customers.router, invoices.router, payments.router, analytics.router, subscriptions.router, admin.router]:
    app.include_router(router, prefix=settings.api_v1_prefix)

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env, "version": "4.0.0"}
