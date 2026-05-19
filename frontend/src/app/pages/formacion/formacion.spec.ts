import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Formacion } from './formacion';

describe('Formacion', () => {
  let component: Formacion;
  let fixture: ComponentFixture<Formacion>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Formacion],
    }).compileComponents();

    fixture = TestBed.createComponent(Formacion);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
