from __future__ import annotations
from typing import Optional, List
from datetime import date
from pydantic import BaseModel
from .contact_schema import ContactCreateSchema, ContactSchema

class InvoiceLineCreateSchema(BaseModel):
    description: Optional[str] = None
    count: Optional[int] = None
    unit_cost: Optional[float] = None
    line_amount: Optional[float] = None

    class Config:
        orm_mode = True

class InvoiceLineSchema(InvoiceLineCreateSchema):
    id: int
    invoice_id: int

class InvoiceCreateSchema(BaseModel):
    invoice_number: str
    invoice_date: date
    amount: float
    tax: float
    invoice_lines: List[InvoiceLineCreateSchema]
    payor: 'ContactCreateSchema'
    payee: 'ContactCreateSchema'

    class Config:
        orm_mode = True

class InvoiceUpdateSchema(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    amount: Optional[float] = None
    tax: Optional[float] = None
    invoice_lines: Optional[List[InvoiceLineSchema]] = None
    payor: Optional['ContactCreateSchema'] = None
    payee: Optional['ContactCreateSchema'] = None

    class Config:
        orm_mode = True

class InvoiceSchema(BaseModel):
    id: int
    invoice_number: str
    invoice_date: date
    amount: float
    tax: float
    payor_id: int
    payee_id: int
    invoice_lines: List[InvoiceLineSchema]
    payor: ContactSchema
    payee: ContactSchema
    # invoice_image: Optional[bytes] = None
    from_llm: bool

    class Config:
        orm_mode = True
    
    
from .contact_schema import ContactSchema, ContactCreateSchema