import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Planeamiento } from './planeamiento';

describe('Planeamiento', () => {
  let component: Planeamiento;
  let fixture: ComponentFixture<Planeamiento>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Planeamiento],
    }).compileComponents();

    fixture = TestBed.createComponent(Planeamiento);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
