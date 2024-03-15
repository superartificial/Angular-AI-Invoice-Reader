import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InvoiceLine } from '../models/invoice.model';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-invoice-lines',
  templateUrl: './invoice-lines.component.html',
  standalone: true,
  imports: [ FormsModule, CommonModule ],  
})
export class InvoiceLinesComponent {
  @Input() invoiceLines: InvoiceLine[] = [];
  @Output() invoiceLinesChange = new EventEmitter<InvoiceLine[]>();

  addLine() {
    const newLine: InvoiceLine = {
      description: '',
      count: 0,
      unit_cost: 0,
      line_amount: 0
    };

    this.invoiceLines.push(newLine);
    this.invoiceLinesChange.emit(this.invoiceLines);
  }

  deleteLine(index: number) {
    this.invoiceLines.splice(index, 1);
    this.invoiceLinesChange.emit(this.invoiceLines);
  }

  calculateLineAmount(index: number) {
    const line = this.invoiceLines[index];
    line.line_amount = line.count * line.unit_cost;
  }
}