import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, create_tables, Invoice, InvoiceLine, Contact
from schemas import InvoiceSchema, InvoiceCreateSchema
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

def get_or_create_contact(db: Session, contact_data: dict):
    contact = db.query(Contact).filter_by(
        name=contact_data["name"],
        line1=contact_data["line1"],
        line2=contact_data.get("line2"),
        city=contact_data["city"],
        country=contact_data["country"],
        postcode=contact_data["postcode"],
        phone_number=contact_data["phone_number"],
        email=contact_data["email"]
    ).first()

    if not contact:
        contact = Contact(**contact_data)
        db.add(contact)
        db.flush()

    return contact

@app.post("/invoices", response_model=InvoiceSchema)
def create_or_update_invoice(invoice: InvoiceSchema, db: Session = Depends(get_db)):
    payor_data = invoice.payor.dict(exclude={"id"})
    payee_data = invoice.payee.dict(exclude={"id"})
    invoice_lines_data = [line.dict(exclude={"id"}) for line in invoice.invoice_lines]

    if invoice.id == -1:
        # Create new invoice
        payor = get_or_create_contact(db, payor_data)
        payee = get_or_create_contact(db, payee_data)

        invoice_data = invoice.dict(exclude={"payor", "payee", "invoice_lines", "id"})
        invoice_db = Invoice(**invoice_data, payor_id=payor.id, payee_id=payee.id)
        db.add(invoice_db)
        db.flush()

        for line_data in invoice_lines_data:
            invoice_line = InvoiceLine(**line_data, invoice_id=invoice_db.id)
            db.add(invoice_line)
    else:
        # Update existing invoice
        invoice_db = db.query(Invoice).filter(Invoice.id == invoice.id).first()
        if not invoice_db:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Update contact details
        payor = get_or_create_contact(db, payor_data)
        payee = get_or_create_contact(db, payee_data)

        invoice_data = invoice.dict(exclude={"payor", "payee", "invoice_lines", "id"})
        for key, value in invoice_data.items():
            setattr(invoice_db, key, value)

        invoice_db.payor_id = payor.id
        invoice_db.payee_id = payee.id

        # Update invoice lines
        existing_line_ids = [line.id for line in invoice_db.invoice_lines]
        updated_line_ids = []

        for line_data in invoice_lines_data:
            if "id" in line_data and line_data["id"] in existing_line_ids:
                # Update existing line
                line_id = line_data.pop("id")
                db.query(InvoiceLine).filter(InvoiceLine.id == line_id).update(line_data)
                updated_line_ids.append(line_id)
            else:
                # Create new line
                invoice_line = InvoiceLine(**line_data, invoice_id=invoice_db.id)
                db.add(invoice_line)

        # Delete lines that are not in the updated data
        deleted_line_ids = set(existing_line_ids) - set(updated_line_ids)
        if deleted_line_ids:
            db.query(InvoiceLine).filter(InvoiceLine.id.in_(deleted_line_ids)).delete(synchronize_session=False)

    db.commit()
    db.refresh(invoice_db)

    return invoice_db

@app.get("/invoices/{invoice_id}", response_model=InvoiceSchema)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice