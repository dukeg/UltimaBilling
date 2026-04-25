import json
from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..deps import get_current_user
from .. import models, schemas
from ..services.payments import verify_stripe_signature, verify_razorpay_signature, normalize_provider_event
from ..services.audit import record

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/checkout")
def create_checkout(payload: schemas.CheckoutRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    inv = db.query(models.Invoice).filter_by(id=payload.invoice_id, organization_id=user.organization_id).first()
    if not inv: raise HTTPException(404, "Invoice not found")
    if payload.provider not in {"stripe", "razorpay"}: raise HTTPException(400, "Unsupported provider")
    # Integration point: create a real Stripe Checkout Session or Razorpay order after adding live keys.
    return {"provider": payload.provider, "invoice_id": inv.id, "amount": inv.total, "currency": inv.currency, "metadata": {"invoice_id": str(inv.id), "org_id": str(user.organization_id)}}

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str | None = Header(default=None), db: Session = Depends(get_db)):
    raw = await request.body()
    if not verify_stripe_signature(raw, stripe_signature or ""):
        raise HTTPException(400, "Invalid Stripe signature")
    return process_event("stripe", json.loads(raw), db)

@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request, x_razorpay_signature: str | None = Header(default=None), db: Session = Depends(get_db)):
    raw = await request.body()
    if not verify_razorpay_signature(raw, x_razorpay_signature or ""):
        raise HTTPException(400, "Invalid Razorpay signature")
    return process_event("razorpay", json.loads(raw), db)

def process_event(provider: str, payload: dict, db: Session):
    data = normalize_provider_event(provider, payload)
    existing = db.query(models.Payment).filter_by(provider=provider, provider_event_id=data["event_id"]).first()
    if existing: return {"status": "duplicate_ignored"}
    invoice = db.query(models.Invoice).filter_by(id=int(data["invoice_id"] or 0)).first()
    pay = models.Payment(organization_id=invoice.organization_id if invoice else 1, invoice_id=invoice.id if invoice else None, provider=provider, provider_event_id=data["event_id"], provider_payment_id=data.get("payment_id"), provider_order_id=data.get("order_id"), amount=data["amount"], currency=data["currency"], status=data["status"], raw_payload=json.dumps(payload))
    db.add(pay)
    if invoice and ("paid" in data["status"] or "checkout.session.completed" == data["status"]):
        invoice.status = "paid"; invoice.paid_at = datetime.utcnow()
        record(db, invoice.organization_id, None, "invoice.paid", "invoice", str(invoice.id), provider)
    db.commit()
    return {"status": "processed"}
