from datetime import date
from pydantic import BaseModel
from typing import List, Optional

class ContactSchema(BaseModel):
    id: Optional[int]
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
    id: Optional[int]
    description: Optional[str] = None
    count: Optional[int]
    unit_cost: Optional[float]
    line_amount: Optional[float]

    class Config:
        orm_mode = True

class InvoiceSchema(BaseModel):
    id: int
    invoice_number: str
    invoice_date: date
    amount: Optional[float]
    tax: Optional[float]
    invoice_lines: List[InvoiceLineSchema]
    payor: ContactSchema
    payee: ContactSchema

    class Config:
        orm_mode = True
        
class InvoiceCreateSchema(BaseModel):
    invoice_number: str
    invoice_date: date
    amount: float
    tax: float
    invoice_lines: List[InvoiceLineSchema]
    payor: ContactSchema
    payee: ContactSchema

    class Config:
        orm_mode = True        
        
class ContactSchema(BaseModel):
    id: Optional[int]
    name: str
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    payee_invoice_count: int
    payor_invoice_count: int

    class Config:
        orm_mode = True