import { TestBed } from '@angular/core/testing';

import { Rq } from './rq';

describe('Rq', () => {
  let service: Rq;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Rq);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
