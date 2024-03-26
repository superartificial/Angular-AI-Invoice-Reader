from sqlalchemy.orm import Session
from database import engine

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./invoices.db"

PG_SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://postgres:pg16@localhost:5432/invoice_reader'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

pg_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base = declarative_base()

def get_db():
    db = Session(autocommit=False, autoflush=False, bind=engine)
    try:
        yield db
    finally:
        db.close()