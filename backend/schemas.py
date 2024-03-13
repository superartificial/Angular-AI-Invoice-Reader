from datetime import date
from pydantic import BaseModel
from typing import List, Optional

class ContactSchema(BaseModel):
    id: int
    name: str
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True

class InvoiceLineSchema(BaseModel):
    id: int
    description: str
    count: int
    unit_cost: float
    line_amount: float

    class Config:
        orm_mode = True

class InvoiceSchema(BaseModel):
    id: int
    invoice_number: str
    invoice_date: date
    amount: float
    tax: float
    invoice_lines: List[InvoiceLineSchema]
    payor: ContactSchema
    payee: ContactSchema

    class Config:
        orm_mode = True