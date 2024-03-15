import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InvoiceService } from '../services/invoice.service';
import { Invoice } from '../models/invoice.model';
import { NgxPaginationModule } from 'ngx-pagination';
import { Router } from '@angular/router';

@Component({
  selector: 'app-invoices',
  templateUrl: './invoices.component.html',
  styleUrls: ['./invoices.component.scss'],
  standalone: true,
  imports: [CommonModule, NgxPaginationModule]
})
export class InvoicesComponent implements OnInit {
  invoices: Invoice[] = [];
  currentPage = 1;
  pageSize = 10;  

  constructor(private invoiceService: InvoiceService, private router: Router) { }

  ngOnInit(): void {
    console.log('in invoice list')
    this.getInvoices();
  }

  getInvoices(): void {
    this.invoiceService.getInvoices()
      .subscribe(invoices => this.invoices = invoices);
  }

  editInvoice(invoiceId: number): void {
    this.router.navigate(['/new-invoice', invoiceId]);
  }

}