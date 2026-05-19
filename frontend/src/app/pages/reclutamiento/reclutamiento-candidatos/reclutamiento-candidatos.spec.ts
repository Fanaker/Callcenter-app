import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReclutamientoCandidatos } from './reclutamiento-candidatos';

describe('ReclutamientoCandidatos', () => {
  let component: ReclutamientoCandidatos;
  let fixture: ComponentFixture<ReclutamientoCandidatos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReclutamientoCandidatos],
    }).compileComponents();

    fixture = TestBed.createComponent(ReclutamientoCandidatos);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
