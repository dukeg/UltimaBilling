from datetime import datetime
from sqlalchemy.orm import Session
from .. import models

def invoice_number(org_id: int) -> str:
    return f"INV-{org_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

def create_invoice(db: Session, org_id: int, payload):
    subtotal = sum(i.quantity * i.unit_price for i in payload.items)
    total = max(subtotal + payload.tax - payload.discount, 0)
    inv = models.Invoice(organization_id=org_id, customer_id=payload.customer_id, invoice_number=invoice_number(org_id), currency=payload.currency, subtotal=subtotal, tax=payload.tax, discount=payload.discount, total=total, notes=payload.notes, due_date=payload.due_date, subscription_id=payload.subscription_id, status="issued")
    db.add(inv); db.flush()
    for i in payload.items:
        db.add(models.InvoiceItem(invoice_id=inv.id, description=i.description, quantity=i.quantity, unit_price=i.unit_price, amount=i.quantity*i.unit_price))
    return inv
