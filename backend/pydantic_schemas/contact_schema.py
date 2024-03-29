from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel

class ContactCreateSchema(BaseModel):
    name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_city: Optional[str] = None
    address_country: Optional[str] = None
    address_postcode: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True

class ContactSchema(ContactCreateSchema):
    id: int
