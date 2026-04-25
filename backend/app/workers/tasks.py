from datetime import date, timedelta
from sqlalchemy.orm import Session
from .celery_app import celery
from ..core.database import SessionLocal
from .. import models, schemas
from ..services.billing import create_invoice
from ..services.pdf import render_invoice_pdf

INTERVAL_DAYS = {"weekly": 7, "monthly": 30, "quarterly": 90, "yearly": 365}

@celery.task
def generate_recurring_invoices():
    db: Session = SessionLocal()
    created = 0
    try:
        today = date.today().isoformat()
        subs = db.query(models.Subscription).filter(models.Subscription.status == "active", models.Subscription.next_run_date <= today).all()
        for sub in subs:
            payload = schemas.InvoiceCreate(customer_id=sub.customer_id, currency=sub.currency, tax=0, discount=0, notes=f"Recurring invoice for {sub.name}", due_date=None, subscription_id=sub.id, items=[schemas.InvoiceItemIn(description=sub.name, quantity=1, unit_price=sub.amount)])
            inv = create_invoice(db, sub.organization_id, payload)
            db.flush()
            customer = db.query(models.Customer).filter_by(id=sub.customer_id).first()
            inv.pdf_url = render_invoice_pdf(inv, customer, inv.items)
            sub.next_run_date = (date.today() + timedelta(days=INTERVAL_DAYS.get(sub.interval, 30))).isoformat()
            if sub.cancel_at_period_end:
                sub.status = "canceled"
            created += 1
        db.commit()
        return {"created": created}
    finally:
        db.close()

@celery.task
def mark_overdue_invoices():
    db = SessionLocal()
    try:
        today = date.today().isoformat()
        rows = db.query(models.Invoice).filter(models.Invoice.status.in_(["issued", "sent"]), models.Invoice.due_date != None, models.Invoice.due_date < today).all()
        for inv in rows:
            inv.status = "overdue"
        db.commit()
        return {"marked_overdue": len(rows)}
    finally:
        db.close()
