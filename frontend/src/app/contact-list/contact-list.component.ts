import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Contact } from '../models/contact.model';
import { ContactService } from '../services/contact.service';
import { NgxPaginationModule } from 'ngx-pagination';

@Component({
  selector: 'app-contact-list',
  standalone: true,
  imports: [CommonModule, NgxPaginationModule],
  templateUrl: './contact-list.component.html',
  styleUrls: ['./contact-list.component.scss']
})
export class ContactListComponent implements OnInit {
  contacts: Contact[] = [];

  contacts_data: {contact: Contact, payee_invoice_count: number, payor_invoice_count: number}[] = [];

  currentPage = 1;
  pageSize = 10;

  constructor(private contactService: ContactService) { }

  ngOnInit(): void {
    this.getContacts();
  }

  getContacts(): void {
    this.contactService.getContacts()
      .subscribe(contacts_data => this.contacts_data = contacts_data);
  }
}