import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, create_tables, Invoice
from schemas import InvoiceSchema
from sqlalchemy.orm import Session

app = FastAPI()

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

'''@app.on_event("startup")
def startup_event():
    create_tables()
    with Session(bind=engine) as db:
        with open("invoices.json", "r") as file:
            invoices_data = json.load(file)
            for invoice_data in invoices_data:
                invoice = Invoice(**invoice_data)
                db.add(invoice)
            db.commit()'''

@app.get("/invoices", response_model=list[InvoiceSchema])
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    return invoices