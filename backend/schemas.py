from datetime import date
from pydantic import BaseModel

class InvoiceSchema(BaseModel):
    id: int
    customer_name: str
    invoice_number: str
    invoice_date: date
    amount: float
    tax: float

    class Config:
        orm_mode = True