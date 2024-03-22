from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./invoices.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    line1 = Column(String, nullable=True)
    line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)

class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    count = Column(Integer, nullable=True)
    unit_cost = Column(Float, nullable=True)
    line_amount = Column(Float, nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, index=True)
    invoice_date = Column(Date, nullable=True)
    amount = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    payor_id = Column(Integer, ForeignKey("contacts.id"))
    payee_id = Column(Integer, ForeignKey("contacts.id"))

    invoice_lines = relationship("InvoiceLine", backref="invoice")
    payor = relationship("Contact", foreign_keys=[payor_id])
    payee = relationship("Contact", foreign_keys=[payee_id])
    invoice_image = Column(LargeBinary, nullable=True)    

def create_tables():
    Base.metadata.create_all(bind=engine)
    
def clear_all():
    Base.metadata.drop_all(bind=engine)
    # Recreate the tables
    Base.metadata.create_all(bind=engine)
