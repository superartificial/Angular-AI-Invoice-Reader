import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { InvoiceService } from '../services/invoice.service';
import { Invoice, InvoiceLine } from '../models/invoice.model';
import { ContactFormSectionComponent } from '../contact-form-section/contact-form-section.component';
import { InvoiceLinesComponent } from '../invoice-lines/invoice-lines.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-new-invoice-form',
  templateUrl: './new-invoice-form.component.html',
  styleUrls: ['./new-invoice-form.component.scss'],
  standalone: true,
  imports: [ ContactFormSectionComponent, InvoiceLinesComponent, FormsModule ]
})
export class NewInvoiceFormComponent implements OnInit {
  invoice: Invoice = {
    invoice_number: '',
    invoice_date: new Date(),
    amount: 0,
    tax: 0,
    payor: {
      name: '',
      line1: '',
      line2: '',
      city: '',
      country: '',
      postcode: '',
      phone_number: '',
      email: ''
    },
    payee: {
      name: '',
      line1: '',
      line2: '',
      city: '',
      country: '',
      postcode: '',
      phone_number: '',
      email: ''
    },
    invoice_lines: []
  };

  constructor(private invoiceService: InvoiceService, private router: Router) { }

  ngOnInit(): void {
  }

  onSubmit(): void {
    console.log('submitting')
    this.invoiceService.createInvoice(this.invoice)
      .subscribe(
        response => {
          console.log('Invoice created successfully:', response);
          this.router.navigate(['/invoices']);
        },
        error => {
          console.error('Error creating invoice:', error);
        }
      );
  }

  onCancel(): void {
    this.router.navigate(['/invoices']);
  }
}