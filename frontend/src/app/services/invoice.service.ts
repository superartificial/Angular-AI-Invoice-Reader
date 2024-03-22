import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Invoice } from '../models/invoice.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class InvoiceService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getInvoices(): Observable<Invoice[]> {
    return this.http.get<Invoice[]>(`${this.apiUrl}/invoices`);
  }

  getInvoice(invoiceId: number): Observable<Invoice> {
    return this.http.get<Invoice>(`${this.apiUrl}/invoices/${invoiceId}`);
  }
  
  updateInvoice(invoice: Invoice): Observable<Invoice> {
    return this.http.post<Invoice>(`${this.apiUrl}/invoices`, invoice);
  }  

  createInvoice(invoice: Invoice): Observable<Invoice> {
    return this.http.post<Invoice>(`${this.apiUrl}/invoices`, invoice);
  }

  getInvoiceImage(invoiceId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/invoices/${invoiceId}/image`, { responseType: 'blob' });
  }

}