from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://invoice_reader_user:2exCFtiAs8t0Xd0uyfMl7qePVFzvCSK9@dpg-co2udi6v3ddc73dljat0-a.singapore-postgres.render.com/invoice_reader'
# SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://postgres:pg16@localhost:5432/invoice_reader'

engine = create_engine(
   SQLALCHEMY_DATABASE_URL, connect_args={}, future=True
)
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    future=True
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    