from typing import List, Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "member"

class CustomerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    billing_address: str = ""

class CustomerOut(CustomerCreate):
    id: int
    class Config: from_attributes = True

class InvoiceItemIn(BaseModel):
    description: str
    quantity: float = 1
    unit_price: float = 0

class InvoiceCreate(BaseModel):
    customer_id: int
    currency: str = "INR"
    tax: float = 0
    discount: float = 0
    notes: str = ""
    due_date: Optional[str] = None
    subscription_id: Optional[int] = None
    items: List[InvoiceItemIn]

class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    status: str
    total: float
    currency: str
    pdf_url: Optional[str] = None
    class Config: from_attributes = True

class SubscriptionCreate(BaseModel):
    customer_id: int
    name: str
    amount: float
    currency: str = "INR"
    interval: str = "monthly"
    next_run_date: str
    trial_ends_at: Optional[str] = None
    notes: str = ""

class CheckoutRequest(BaseModel):
    invoice_id: int
    provider: str
