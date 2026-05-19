import { Postulante } from './postulante.model';

export type EstadoRq = 'ABIERTO' | 'CERRADO';

export interface Rq {
  codigo: string;

  campaniaId: number;
  campaign: string;

  puestoId: number;
  puesto: string;

  comentarios: string;
  cantidad: number;
  diasCapacitacion: number;

  fechaIngreso: string;
  fechaInicioCapacitacion: string;
  fechaFinCapacitacion: string;

  estado: EstadoRq;

  testCount: number;
  aprobacionPromedio: number;
  applyPath: string;

  candidatos: Postulante[];
}