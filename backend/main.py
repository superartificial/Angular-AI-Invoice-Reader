import json
import google.generativeai as genai
import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models.contact_model import Contact
from db.models.invoice_model import Invoice, InvoiceLine
from datetime import datetime
from prompts import input_prompt
from dotenv import load_dotenv
from db.db_setup import get_db, engine
from api.utils.llm_functions import input_image_details, get_gemini_response

from pydantic_schemas.invoice_schema import InvoiceCreateSchema, InvoiceUpdateSchema, InvoiceSchema
from pydantic_schemas.contact_schema import ContactCreateSchema

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()

# CORS configuration
origins = [
    os.getenv("FRONTEND_URL")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/import-invoices")
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


def get_or_create_contact(db: Session, contact_data: dict):
    
    # This lookup probably is not necessary
    contact = db.query(Contact).filter_by(
        name=contact_data.get("name"),
        address_line1=contact_data.get("address_line1"),
        address_line2=contact_data.get("address_line2"),
        address_city=contact_data.get("address_city"),
        address_country=contact_data.get("address_country"),
        address_postcode=contact_data.get("address_postcode"),
        phone_number=contact_data.get("phone_number"),
        email=contact_data.get("email")
    ).first()

    if not contact:
        contact = Contact(**contact_data)
        db.add(contact)
        db.flush()

    return contact


from pydantic_schemas.invoice_schema import InvoiceCreateSchema, InvoiceUpdateSchema, InvoiceSchema
from pydantic_schemas.contact_schema import ContactCreateSchema

@app.post("/invoices", response_model=InvoiceSchema)
def create_invoice(invoice: InvoiceCreateSchema, db: Session = Depends(get_db)):
    payor_data = invoice.payor.dict()
    payee_data = invoice.payee.dict()
    invoice_lines_data = [line.dict() for line in invoice.invoice_lines]

    invoice_data = invoice.dict(exclude={"payor", "payee", "invoice_lines"})

    # Create new invoice
    payor = get_or_create_contact(db, payor_data)
    payee = get_or_create_contact(db, payee_data)

    invoice_db = Invoice(**invoice_data, payor_id=payor.id, payee_id=payee.id)
    db.add(invoice_db)
    db.flush()

    # Create invoice lines
    for line_data in invoice_lines_data:
        invoice_line = InvoiceLine(**line_data, invoice_id=invoice_db.id)
        db.add(invoice_line)

    db.commit()
    db.refresh(invoice_db)

    return invoice_db

@app.put("/invoices/{invoice_id}", response_model=InvoiceSchema)
def update_invoice(invoice_id: int, invoice: InvoiceUpdateSchema, db: Session = Depends(get_db)):
    invoice_db = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice_db:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice_data = invoice.dict(exclude_unset=True, exclude={"payor", "payee", "invoice_lines"})

    # Update invoice fields
    for key, value in invoice_data.items():
        setattr(invoice_db, key, value)

    # Update contact details
    if invoice.payor:
        payor_data = invoice.payor.dict()
        payor = get_or_create_contact(db, payor_data)
        invoice_db.payor_id = payor.id

    if invoice.payee:
        payee_data = invoice.payee.dict()
        payee = get_or_create_contact(db, payee_data)
        invoice_db.payee_id = payee.id

    # Update invoice lines
    if invoice.invoice_lines:
        existing_line_ids = [line.id for line in invoice_db.invoice_lines]
        updated_line_ids = []

        for line_data in invoice.invoice_lines:
            line_id = line_data.id
            if line_id in existing_line_ids:
                # Update existing line
                db.query(InvoiceLine).filter(InvoiceLine.id == line_id).update(line_data.dict(exclude={"id"}))
                updated_line_ids.append(line_id)
            else:
                # Create new line
                invoice_line = InvoiceLine(**line_data.dict(exclude={"id"}), invoice_id=invoice_db.id)
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
    invoices = db.query(Invoice).all()
    return [
        {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date,
            "amount": invoice.amount,
            "tax": invoice.tax,
            "payor_id": invoice.payor_id,
            "payee_id": invoice.payee_id,
            "from_llm": invoice.from_llm,
            "payor": db.query(Contact).filter(Contact.id == invoice.payor_id).first(),
            "payee": db.query(Contact).filter(Contact.id == invoice.payee_id).first(),
            "invoice_lines": invoice.invoice_lines
        }
        for invoice in invoices
    ]
    
    
@app.get("/invoices/{invoice_id}/image")
def get_invoice_image(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return Response(content=invoice.invoice_image, media_type="image/jpeg")


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
    if image_data:
        invoice.invoice_image = image_data      
    
    # Create invoice lines
    invoice_lines = []
    for line_data in invoice_lines_data:
        invoice_line = InvoiceLine(**line_data)
        invoice_lines.append(invoice_line)
    
    invoice.invoice_lines = invoice_lines
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    return invoice

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
        
        print(json_string)
        
        invoice_data = json.loads(json_string)                
        ai_comments = invoice_data.pop("ai_comments")
        
        # if(invoice_data['invoice_number'] or invoice_data['payor'] or invoice_data['payee']):        
            # Save invoice data to the database
        invoice_dict = create_invoice(db, invoice_data, image_data[0]['data'])
        invoiceid = invoice_dict.id
        # else:
        #     invoiceid = ''    
        
        response = { "id": invoiceid, "ai_comments": ai_comments }  
    else:
        response = {}  # Or any other appropriate default value or error handling    
        
    return response
        
        