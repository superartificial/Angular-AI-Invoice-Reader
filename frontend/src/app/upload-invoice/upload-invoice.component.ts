import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-upload-invoice',
  templateUrl: './upload-invoice.component.html',
  styleUrls: ['./upload-invoice.component.scss']
})
export class UploadInvoiceComponent {
  selectedFile: File | null = null;

  constructor(private http: HttpClient, private router: Router) { }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  onSubmit() {
    if (this.selectedFile) {
      const formData = new FormData();
      formData.append('file', this.selectedFile, this.selectedFile.name);

      this.http.post('http://localhost:8000/upload', formData).subscribe(
        (res: any) => {
          console.log('File uploaded successfully',res);
          this.router.navigate(['/new-invoice', res.id]);
        },
        (error) => {
          console.error('Error uploading file:', error);
          // Handle error response
        }
      );
    }
  }
}