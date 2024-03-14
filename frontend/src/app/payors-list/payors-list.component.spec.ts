import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PayorsListComponent } from './payors-list.component';

describe('PayorsListComponent', () => {
  let component: PayorsListComponent;
  let fixture: ComponentFixture<PayorsListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PayorsListComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PayorsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
