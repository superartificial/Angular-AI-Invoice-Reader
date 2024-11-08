import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Contact } from '../models/contact.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ContactService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getContacts(): Observable<{contact: Contact, payee_invoice_count: number, payor_invoice_count: number}[]> {
    return this.http.get<{contact: Contact, payee_invoice_count: number, payor_invoice_count: number}[]>(`${this.apiUrl}/contacts`);
  }
}