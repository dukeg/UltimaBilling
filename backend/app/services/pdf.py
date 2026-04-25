from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .storage import save_pdf

def render_invoice_pdf(invoice, customer, items) -> str:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, f"Invoice {invoice.invoice_number}")
    c.setFont("Helvetica", 11)
    c.drawString(50, 775, f"Customer: {customer.name}")
    c.drawString(50, 760, f"Email: {customer.email or '-'}")
    y = 720
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Description")
    c.drawString(330, y, "Qty")
    c.drawString(380, y, "Unit")
    c.drawString(450, y, "Amount")
    c.setFont("Helvetica", 10)
    for item in items:
        y -= 22
        c.drawString(50, y, item.description[:45])
        c.drawString(330, y, str(item.quantity))
        c.drawString(380, y, f"{item.unit_price:.2f}")
        c.drawString(450, y, f"{item.amount:.2f}")
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(380, y, f"Total: {invoice.currency} {invoice.total:.2f}")
    c.showPage(); c.save()
    return save_pdf(invoice.invoice_number, buf.getvalue())
