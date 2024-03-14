import { Component, Input } from '@angular/core';
import { Contact } from '../models/contact.model';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-contact-form-section',
  standalone: true,
  imports: [ FormsModule ],
  templateUrl: './contact-form-section.component.html',
  styleUrl: './contact-form-section.component.scss'
})
export class ContactFormSectionComponent {
  @Input() title: string = '';
  @Input() identifier: string = '';
  @Input() contact: Contact = {
    name: '',
    line1: '',
    line2: '',
    city: '',
    country: '',
    postcode: '',
    phone_number: '',
    email: ''
  };
}