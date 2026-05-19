import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Reclutamiento } from './reclutamiento';

describe('Reclutamiento', () => {
  let component: Reclutamiento;
  let fixture: ComponentFixture<Reclutamiento>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Reclutamiento],
    }).compileComponents();

    fixture = TestBed.createComponent(Reclutamiento);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
