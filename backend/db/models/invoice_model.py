from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import Integer, String, Float, ForeignKey, LargeBinary, Boolean, DateTime
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..db_setup import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String, index=True)
    invoice_date: Mapped[Optional[date]]
    amount: Mapped[Optional[float]] = mapped_column(Float)
    tax: Mapped[Optional[float]] = mapped_column(Float)
    payor_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    payee_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    from_llm: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    invoice_lines: Mapped[List["InvoiceLine"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )    
        
    payor: Mapped["Contact"] = relationship(foreign_keys=[payor_id])
    payee: Mapped["Contact"] = relationship(foreign_keys=[payee_id])
    invoice_image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(String)
    count: Mapped[Optional[int]] = mapped_column(Integer)
    unit_cost: Mapped[Optional[float]] = mapped_column(Float)
    line_amount: Mapped[Optional[float]] = mapped_column(Float)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    
    invoice: Mapped["Invoice"] = relationship(back_populates="invoice_lines")