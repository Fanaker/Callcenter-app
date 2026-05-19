import { Rq } from '../models/rq.model';
import { POSTULANTES_MOCK } from './postulantes.mock';

export const RQS_MOCK: Rq[] = [
  {
    codigo: 'RQ001',
    campaniaId: 1,
    campaign: 'Renovación Proactiva',
    puestoId: 1,
    puesto: 'Asesor de ventas',
    comentarios: 'Requerimiento para campaña comercial outbound.',
    cantidad: 10,
    diasCapacitacion: 10,
    fechaIngreso: '2026-06-01',
    fechaInicioCapacitacion: '2026-05-25',
    fechaFinCapacitacion: '2026-05-30',
    estado: 'ABIERTO',
    testCount: 3,
    aprobacionPromedio: 11,
    applyPath: '/postular/RQ001',
    candidatos: POSTULANTES_MOCK.filter((p) => p.rqCodigo === 'RQ001')
  },
  {
    codigo: 'RQ002',
    campaniaId: 3,
    campaign: 'Upselling',
    puestoId: 1,
    puesto: 'Asesor de ventas',
    comentarios: 'Requerimiento para refuerzo de ventas.',
    cantidad: 5,
    diasCapacitacion: 7,
    fechaIngreso: '2026-06-15',
    fechaInicioCapacitacion: '2026-06-05',
    fechaFinCapacitacion: '2026-06-12',
    estado: 'ABIERTO',
    testCount: 3,
    aprobacionPromedio: 10,
    applyPath: '/postular/RQ002',
    candidatos: POSTULANTES_MOCK.filter((p) => p.rqCodigo === 'RQ002')
  },
  {
    codigo: 'RQ003',
    campaniaId: 5,
    campaign: 'Campaña Fin de Año',
    puestoId: 3,
    puesto: 'Back Office',
    comentarios: 'RQ histórico cerrado para pruebas.',
    cantidad: 3,
    diasCapacitacion: 5,
    fechaIngreso: '2026-04-15',
    fechaInicioCapacitacion: '2026-04-01',
    fechaFinCapacitacion: '2026-04-05',
    estado: 'CERRADO',
    testCount: 4,
    aprobacionPromedio: 12,
    applyPath: '/postular/RQ003',
    candidatos: POSTULANTES_MOCK.filter((p) => p.rqCodigo === 'RQ003')
  }
];