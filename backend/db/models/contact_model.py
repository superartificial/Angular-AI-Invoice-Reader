from typing import List, Optional
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship

from ..db_setup import Base

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String, index=True)
    address_line1: Mapped[Optional[str]]
    address_line2: Mapped[Optional[str]]
    address_city: Mapped[Optional[str]]
    address_country: Mapped[Optional[str]]
    address_postcode: Mapped[Optional[str]]
    phone_number: Mapped[Optional[str]]
    email: Mapped[Optional[str]]

    invoices_as_payor: Mapped[List["Invoice"]] = relationship(
        back_populates="payor",
        foreign_keys="Invoice.payor_id",  # Add this line
        uselist=False
    )

    invoices_as_payee: Mapped[List["Invoice"]] = relationship(
        back_populates="payee",
        foreign_keys="Invoice.payee_id",  # Add this line
        uselist=False
    )