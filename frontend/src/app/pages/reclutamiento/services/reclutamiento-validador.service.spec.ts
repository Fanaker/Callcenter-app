import { TestBed } from '@angular/core/testing';
import { ReclutamientoValidadorService } from './reclutamiento-validador.service';

/**
 * Tests para el servicio de validación de reclutamiento
 * Verifica la regla: Entrevista "Sí" solo cuando Apto = "Sí"
 */
describe('ReclutamientoValidadorService', () => {
  let service: ReclutamientoValidadorService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ReclutamientoValidadorService]
    });
    service = TestBed.inject(ReclutamientoValidadorService);
  });

  it('Debería ser creado', () => {
    expect(service).toBeTruthy();
  });

  describe('validarAptoEntrevista', () => {

    it('Debería permitir apto="si" con cualquier valor de entrevista', () => {
      expect(service.validarAptoEntrevista('si', 'si')).toBe(true);
      expect(service.validarAptoEntrevista('si', 'no')).toBe(true);
      expect(service.validarAptoEntrevista('si', null)).toBe(true);
    });

    it('Debería permitir apto="no" solo con entrevista="no"', () => {
      expect(service.validarAptoEntrevista('no', 'no')).toBe(true);
      expect(service.validarAptoEntrevista('no', 'si')).toBe(false);
      expect(service.validarAptoEntrevista('no', null)).toBe(false);
    });

    it('Debería permitir apto=null solo con entrevista != "si"', () => {
      expect(service.validarAptoEntrevista(null, 'no')).toBe(true);
      expect(service.validarAptoEntrevista(null, null)).toBe(true);
      expect(service.validarAptoEntrevista(null, 'si')).toBe(false);
    });
  });

  describe('corregirEntrevista', () => {

    it('Debería forzar entrevista a "no" cuando apto="no"', () => {
      expect(service.corregirEntrevista('no', 'si')).toBe('no');
      expect(service.corregirEntrevista('no', 'no')).toBe('no');
      expect(service.corregirEntrevista('no', null)).toBe('no');
    });