from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..deps import get_current_user
from ..services.billing import create_invoice
from ..services.pdf import render_invoice_pdf
from ..services.emailer import send_invoice_email
from ..services.audit import record
from .. import models, schemas

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("", response_model=list[schemas.InvoiceOut])
def list_invoices(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Invoice).filter(models.Invoice.organization_id == user.organization_id).order_by(models.Invoice.id.desc()).all()

@router.post("", response_model=schemas.InvoiceOut)
def create(payload: schemas.InvoiceCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    customer = db.query(models.Customer).filter_by(id=payload.customer_id, organization_id=user.organization_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")
    inv = create_invoice(db, user.organization_id, payload)
    db.flush()
    pdf_url = render_invoice_pdf(inv, customer, inv.items)
    inv.pdf_url = pdf_url
    record(db, user.organization_id, user.id, "invoice.created", "invoice", str(inv.id), inv.invoice_number)
    db.commit(); db.refresh(inv)
    return inv

@router.post("/{invoice_id}/send")
def send_invoice(invoice_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    inv = db.query(models.Invoice).filter_by(id=invoice_id, organization_id=user.organization_id).first()
    if not inv: raise HTTPException(404, "Invoice not found")
    customer = db.query(models.Customer).filter_by(id=inv.customer_id).first()
    if not customer or not customer.email: raise HTTPException(400, "Customer email missing")
    send_invoice_email(customer.email, f"Invoice {inv.invoice_number}", f"Your invoice total is {inv.currency} {inv.total}. PDF: {inv.pdf_url}")
    record(db, user.organization_id, user.id, "invoice.sent", "invoice", str(inv.id), customer.email)
    db.commit()
    return {"status": "sent"}
