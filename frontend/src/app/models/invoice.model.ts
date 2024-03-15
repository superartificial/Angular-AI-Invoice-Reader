import { Contact } from "./contact.model";

export interface Invoice {
  id: number;
  invoice_number: string;
  invoice_date: Date;
  amount: number;
  tax: number;
  payor: Contact;
  payee: Contact;
  invoice_lines: InvoiceLine[];
}

export interface InvoiceLine {
  description: string;
  count: number;
  unit_cost: number;
  line_amount: number;
}