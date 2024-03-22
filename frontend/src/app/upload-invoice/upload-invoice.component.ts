import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { DragDropDirective } from '../directives/drag-drop.directive';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-upload-invoice',
  templateUrl: './upload-invoice.component.html',
  styleUrls: ['./upload-invoice.component.scss'],
  imports: [ DragDropDirective, CommonModule ],
  standalone: true
})
export class UploadInvoiceComponent {
  selectedFile: File | null = null;
  aiComment: string = '';

  constructor(private http: HttpClient, private router: Router) { }

  onFileSelected(event: any) {
    console.log(event)
    this.aiComment = '';
    this.selectedFile = (event.target)?event.target.files[0]:event[0];
  }

  onSubmit() {
    if (this.selectedFile) {
      const formData = new FormData();
      formData.append('file', this.selectedFile, this.selectedFile.name);

      this.http.post(`${environment.apiUrl}/upload`, formData).subscribe(
        (res: any) => {
          console.log('File uploaded successfully',res);
          this.selectedFile = null;
          this.aiComment = res.ai_comments;
          // this.router.navigate(['/new-invoice', res.id]);
        },
        (error) => {
          console.error('Error uploading file:', error);
          // Handle error response
        }
      );
    }
  }
}