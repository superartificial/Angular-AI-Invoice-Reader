import { Routes } from '@angular/router';
import { InvoiceListComponent } from './invoice-list/invoice-list.component';
import { NewInvoiceFormComponent } from './new-invoice-form/new-invoice-form.component';
import { UploadInvoiceComponent } from './upload-invoice/upload-invoice.component';
import { InvoicesComponent } from './invoices/invoices.component';
import { ContactListComponent } from './contact-list/contact-list.component';

export const routes: Routes = [
    { path: '', redirectTo: '/invoices', pathMatch: 'full' },
    { path: 'invoices', component: InvoicesComponent },
    { path: 'new-invoice', component: NewInvoiceFormComponent },
    { path: 'upload-invoice', component: UploadInvoiceComponent },
    { path: 'contacts', component: ContactListComponent },
    { path: 'new-invoice/:id', component: NewInvoiceFormComponent }
];
