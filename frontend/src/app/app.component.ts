import { Component } from '@angular/core';
import { InvoicesComponent } from './invoices/invoices.component';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  standalone: true,
  imports: [InvoicesComponent,HeaderComponent,FooterComponent,RouterOutlet]
})
export class AppComponent {
  title = 'Invoice Management System';
}