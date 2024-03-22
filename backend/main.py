import json
import google.generativeai as genai
import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine, create_tables, Invoice, InvoiceLine, Contact, clear_all
from schemas import InvoiceSchema, ContactSchema
from datetime import datetime
from prompts import input_prompt
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
from db_functions import get_db
from llm_functions import input_image_details, get_gemini_response
import io
from PIL import Image

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini Pro Vision


app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
 allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # db.query(InvoiceLine).delete()
    # db.query(Invoice).delete()
    # db.query(Contact).delete()
    clear_all()    
    db.commit()
    return {"message": "Data cleared successfully"}

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

@app.get("/invoices", response_model=list[InvoiceSchema])
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice.id, Invoice.invoice_number, Invoice.invoice_date, Invoice.amount, Invoice.tax,
                        Invoice.payor_id, Invoice.payee_id).all()
    return [
        {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date,
            "amount": invoice.amount,
            "tax": invoice.tax,
            "payor": db.query(Contact).filter(Contact.id == invoice.payor_id).first(),
            "payee": db.query(Contact).filter(Contact.id == invoice.payee_id).first(),
            "invoice_lines": db.query(InvoiceLine).filter(InvoiceLine.invoice_id == invoice.id).all()
        }
        for invoice in invoices
    ]
    
@app.get("/invoices/{invoice_id}/image")
def get_invoice_image(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return Response(content=invoice.invoice_image, media_type="image/jpg")    

@app.get("/contacts")
def get_contacts(db: Session = Depends(get_db)):
    contacts = db.query(
        Contact,
        func.count(Invoice.id).filter(Invoice.payee_id == Contact.id).label('payee_invoice_count'),
        func.count(Invoice.id).filter(Invoice.payor_id == Contact.id).label('payor_invoice_count')
    ).group_by(Contact.id).all()

    contact_data = []
    for contact, payee_count, payor_count in contacts:
        contact_dict = {
            'contact': contact,
            'payee_invoice_count': payee_count,
            'payor_invoice_count': payor_count
        }
        contact_data.append(contact_dict)

    return contact_data

@app.get("/invoices/{invoice_id}", response_model=InvoiceSchema)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

def create_invoice(db: Session, invoice_data: dict, image_data: bytes = None):
    # Extract payor and payee data
    payor_data = invoice_data.pop("payor")
    payee_data = invoice_data.pop("payee")
    invoice_lines_data = invoice_data.pop("invoice_lines", [])
    
    # Get or create payor and payee contacts
    payor = get_or_create_contact(db, payor_data)
    payee = get_or_create_contact(db, payee_data)
    
    # Convert invoice_date string to date object
    invoice_date_str = invoice_data.pop("invoice_date")
    invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d").date()
    
    # Create invoice
    invoice = Invoice(**invoice_data, invoice_date=invoice_date, payor_id=payor.id, payee_id=payee.id)
    

    
    # Save the uploaded file to the invoice_image field
    # if image_data:
    #     invoice.invoice_image = image_data      
    
    # Create invoice lines
    invoice_lines = []
    for line_data in invoice_lines_data:
        invoice_line = InvoiceLine(**line_data)
        invoice_lines.append(invoice_line)
    
    invoice.invoice_lines = invoice_lines
    
    print(invoice)    
    
    # db.add(invoice)
    # db.commit()
    # db.refresh(invoice)
    
    return ''

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    '''
    Uploads an invoice file, uses an llm to convert to json, is successful saves in db
    '''
    print('upload')
    temp_upload_dir = "temp_upload"
    os.makedirs(temp_upload_dir, exist_ok=True)
    
    # file_path = os.path.join(temp_upload_dir, file.filename)
    # with open(file_path, "wb") as buffer:
    #     buffer.write(file.read())
    
    image_data = input_image_details(file)
    llm_response = get_gemini_response(input_prompt, image_data, "")
    
    start_index = llm_response.find('{')
    end_index = llm_response.rfind('}')

    if start_index != -1 and end_index != -1:
        json_string = llm_response[start_index:end_index+1]
        #invoice_data = json.loads(json_string)
        print(json_string)
        
        # Save invoice data to the database
        #invoice_dict = create_invoice(db, invoice_data, image_data[0]['data'])
        # del invoice_dict['invoice_image']
        
        response = {} #{ "id": invoice_dict.id }  
    else:
        response = {}  # Or any other appropriate default value or error handling    
        
    return response
        
        