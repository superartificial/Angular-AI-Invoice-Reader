from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./invoices.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
Base = declarative_base()

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    invoice_number = Column(String, index=True)
    invoice_date = Column(Date)
    amount = Column(Float)
    tax = Column(Float)

def create_tables():
    Base.metadata.create_all(bind=engine)