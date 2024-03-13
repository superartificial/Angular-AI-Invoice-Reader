import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, create_tables, Invoice, InvoiceLine, Contact
from schemas import InvoiceSchema
from datetime import datetime

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = Session(autocommit=False, autoflush=False, bind=engine)
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    create_tables()

@app.post("/import-invoices")
def import_invoices(db: Session = Depends(get_db)):
    with open("invoices.json", "r") as file:
        invoices_data = json.load(file)
        for invoice_data in invoices_data:
            payor_data = invoice_data.pop("payor")
            payee_data = invoice_data.pop("payee")
            invoice_lines_data = invoice_data.pop("invoice_lines")

            payor = db.query(Contact).filter_by(name=payor_data["name"]).first()
            if not payor:
                payor = Contact(**payor_data)
                db.add(payor)
                db.flush()

            payee = db.query(Contact).filter_by(name=payee_data["name"]).first()
            if not payee:
                payee = Contact(**payee_data)
                db.add(payee)
                db.flush()

            # Convert invoice_date string to date object
            invoice_date_str = invoice_data.pop("invoice_date")
            invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d").date()

            invoice = Invoice(**invoice_data, invoice_date=invoice_date, payor_id=payor.id, payee_id=payee.id)
            db.add(invoice)
            db.flush()

            for line_data in invoice_lines_data:
                invoice_line = InvoiceLine(**line_data, invoice_id=invoice.id)
                db.add(invoice_line)

    db.commit()
    return {"message": "Invoices imported successfully"}

@app.post("/clear-data")
def clear_data(db: Session = Depends(get_db)):
    db.query(InvoiceLine).delete()
    db.query(Invoice).delete()
    db.query(Contact).delete()
    db.commit()
    return {"message": "Data cleared successfully"}

@app.get("/invoices", response_model=list[InvoiceSchema])
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    return invoices