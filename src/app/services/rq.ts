import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class RqService {
  private rqs: any[] = [
    {
      codigo: 'RQ001',
      campaign: 'Campaña Primavera',
      puesto: 'Ejecutivo de ventas',
      comentarios: 'Puesto para campaña de primavera',
      cantidad: 10,
      diasCapacitacion: 10,
      fechaIngreso: '2026-05-01',
      fechaInicioCapacitacion: '2026-05-10',
      fechaFinCapacitacion: '2026-05-20',
      estado: 'ABIERTO',
      testCount: 3,
      aprobacionPromedio: 11,
      applyPath: '/postular/RQ001',
      candidatos: [
        {
          id: 1,
          nombre: 'Ana',
          apellido: 'Gómez',
          dni: '74125896',
          correo: 'ana.gomez@example.com',
          telefono: '987654321',
          medioPreferido: 'whatsapp',
          cvName: 'ana_gomez_cv.pdf',
          comentarios: 'Disponible para trabajar de inmediato',
          apto: true,
          entrevistaAprobada: true,
          elegido: true,
          contratar: true,
          test1: 8,
          test2: 9,
          test3: 8,
          test4: 11,
          test5: 0
        },
        {
          id: 2,
          nombre: 'Carlos',
          apellido: 'Pérez',
          dni: '74563821',
          correo: 'carlos.perez@example.com',
          telefono: '912345678',
          medioPreferido: 'llamada',
          cvName: 'carlos_perez_cv.pdf',
          comentarios: '',
          apto: false,
          entrevistaAprobada: false,
          elegido: false,
          contratar: false,
          test1: 5,
          test2: 6,
          test3: 5,
          test4: 0,
          test5: 0
        },
        {
          id: 5,
          nombre: 'Bruno',
          apellido: 'López',
          dni: '72345678',
          correo: 'bruno.lopez@example.com',
          telefono: '955112233',
          medioPreferido: 'email',
          cvName: 'bruno_lopez_cv.pdf',
          comentarios: 'Interesado en desarrollo comercial',
          apto: true,
          entrevistaAprobada: true,
          elegido: false,
          contratar: false,
          test1: 7,
          test2: 8,
          test3: 9,
          test4: 0,
          test5: 0
        },
        {
          id: 6,
          nombre: 'Sofía',
          apellido: 'Mendoza',
          dni: '75123489',
          correo: 'sofia.mendoza@example.com',
          telefono: '944776655',
          medioPreferido: 'whatsapp',
          cvName: 'sofia_mendoza_cv.pdf',
          comentarios: 'Disponible fines de semana',
          apto: true,
          entrevistaAprobada: false,
          elegido: false,
          contratar: false,
          test1: 8,
          test2: 7,
          test3: 8,
          test4: 0,
          test5: 0
        }
      ]
    },
    {
      codigo: 'RQ002',
      campaign: 'Campaña Operaciones',
      puesto: 'Asistente administrativo',
      comentarios: 'Necesitamos apoyo para el equipo de operaciones',
      cantidad: 5,
      diasCapacitacion: 7,
      fechaIngreso: '2026-06-01',
      fechaInicioCapacitacion: '2026-06-10',
      fechaFinCapacitacion: '2026-06-15',
      estado: 'ABIERTO',
      testCount: 3,
      aprobacionPromedio: 10,
      applyPath: '/postular/RQ002',
      candidatos: [
        {
          id: 3,
          nombre: 'Laura',
          apellido: 'Martínez',
          dni: '76234519',
          correo: 'laura.martinez@example.com',
          telefono: '944556677',
          medioPreferido: 'email',
          cvName: 'laura_martinez_cv.pdf',
          comentarios: 'Experiencia en atención al cliente',
          apto: true,
          entrevistaAprobada: false,
          elegido: false,
          contratar: false,
          test1: 7,
          test2: 8,
          test3: 7,
          test4: 0,
          test5: 0
        },
        {
          id: 4,
          nombre: 'Diego',
          apellido: 'Ramírez',
          dni: '78123456',
          correo: 'diego.ramirez@example.com',
          telefono: '922334455',
          medioPreferido: 'whatsapp',
          cvName: 'diego_ramirez_cv.pdf',
          comentarios: '',
          apto: true,
          entrevistaAprobada: true,
          elegido: false,
          contratar: true,
          test1: 9,
          test2: 9,
          test3: 8,
          test4: 0,
          test5: 0
        },
        {
          id: 7,
          nombre: 'María',
          apellido: 'Santos',
          dni: '79331234',
          correo: 'maria.santos@example.com',
          telefono: '933221144',
          medioPreferido: 'email',
          cvName: 'maria_santos_cv.pdf',
          comentarios: 'Buena atención al detalle',
          apto: true,
          entrevistaAprobada: true,
          elegido: false,
          contratar: false,
          test1: 8,
          test2: 7,
          test3: 9,
          test4: 0,
          test5: 0
        },
        {
          id: 8,
          nombre: 'Javier',
          apellido: 'Torres',
          dni: '70987654',
          correo: 'javier.torres@example.com',
          telefono: '911223344',
          medioPreferido: 'llamada',
          cvName: 'javier_torres_cv.pdf',
          comentarios: 'Disponible para incorporación inmediata',
          apto: false,
          entrevistaAprobada: false,
          elegido: false,
          contratar: false,
          test1: 6,
          test2: 5,
          test3: 6,
          test4: 0,
          test5: 0
        }
      ]
    },
    {
      codigo: 'RQ003',
      campaign: 'Campaña Fin de Año',
      puesto: 'Coordinador de eventos',
      comentarios: 'Coordinador para eventos corporativos de fin de año',
      cantidad: 3,
      diasCapacitacion: 5,
      fechaIngreso: '2026-04-15',
      fechaInicioCapacitacion: '2026-04-01',
      fechaFinCapacitacion: '2026-04-05',
      estado: 'CERRADO',
      testCount: 4,
      aprobacionPromedio: 12,
      applyPath: '/postular/RQ003',
      candidatos: [
        {
          id: 9,
          nombre: 'Paola',
          apellido: 'Ruiz',
          dni: '70123456',
          correo: 'paola.ruiz@example.com',
          telefono: '988776655',
          medioPreferido: 'whatsapp',
          cvName: 'paola_ruiz_cv.pdf',
          comentarios: 'Gran experiencia en eventos',
          apto: true,
          entrevistaAprobada: true,
          elegido: true,
          contratar: true,
          test1: 12,
          test2: 13,
          test3: 14,
          test4: 13,
          test5: 0
        },
        {
          id: 10,
          nombre: 'Fernando',
          apellido: 'Díaz',
          dni: '70234567',
          correo: 'fernando.diaz@example.com',
          telefono: '977665544',
          medioPreferido: 'email',
          cvName: 'fernando_diaz_cv.pdf',
          comentarios: 'Con experiencia en coordinación logística',
          apto: true,
          entrevistaAprobada: true,
          elegido: false,
          contratar: false,
          test1: 11,
          test2: 12,
          test3: 11,
          test4: 12,
          test5: 0
        },
        {
          id: 11,
          nombre: 'Natalia',
          apellido: 'Cruz',
          dni: '70345678',
          correo: 'natalia.cruz@example.com',
          telefono: '966554433',
          medioPreferido: 'llamada',
          cvName: 'natalia_cruz_cv.pdf',
          comentarios: 'Interesada en coordinación de equipos',
          apto: true,
          entrevistaAprobada: false,
          elegido: false,
          contratar: false,
          test1: 10,
          test2: 9,
          test3: 10,
          test4: 9,
          test5: 0
        }
      ]
    }
  ];

  getAll() {
    const today = new Date();
    for (const rq of this.rqs) {
      const fechaInicio = rq.fechaInicioCapacitacion ? new Date(rq.fechaInicioCapacitacion) : null;
      if (fechaInicio && today >= fechaInicio) {
        rq.estado = 'CERRADO';
      } else {
        rq.estado = 'ABIERTO';
      }
    }
    return this.rqs;
  }

  getByCodigo(codigo: string) {
    const rq = this.rqs.find((rqItem) => rqItem.codigo === codigo);
    if (rq) {
      const today = new Date();
      const fechaInicio = rq.fechaInicioCapacitacion ? new Date(rq.fechaInicioCapacitacion) : null;
      rq.estado = fechaInicio && today >= fechaInicio ? 'CERRADO' : 'ABIERTO';
    }
    return rq;
  }

  add(rq: any) {
    rq.applyPath = '/postular/' + rq.codigo;
    rq.candidatos = [];
    rq.comentarios = rq.comentarios || '';
    rq.campaign = rq.campaign || 'Campaña Sin nombre';
    rq.diasCapacitacion = rq.diasCapacitacion || 1;
    rq.testCount = rq.testCount || 1;
    rq.aprobacionPromedio = rq.aprobacionPromedio || 10;
    rq.estado = 'ABIERTO';
    this.rqs.push(rq);
  }

  generateCode() {
    let max = 0;

    for (let rq of this.rqs) {
      const num = parseInt(rq.codigo.replace('RQ', ''), 10);
      if (num > max) max = num;
    }

    return 'RQ' + String(max + 1).padStart(3, '0');
  }

  toggleStatus(codigo: string) {
    const rq = this.getByCodigo(codigo);
    if (!rq) {
      return;
    }

    rq.estado = rq.estado === 'ABIERTO' ? 'CERRADO' : 'ABIERTO';
  }

  addCandidate(codigo: string, candidate: any) {
    const rq = this.getByCodigo(codigo);
    if (!rq) {
      return;
    }

    const nuevo = {
      id: Date.now(),
      nombre: candidate.nombre,
      apellido: candidate.apellido,
      dni: candidate.dni || '',
      correo: candidate.correo,
      telefono: candidate.telefono,
      medioPreferido: candidate.medioPreferido,
      cvName: candidate.cvName || '',
      comentarios: candidate.comentarios || '',
      apto: false,
      entrevistaAprobada: false,
      elegido: false,
      contratar: false,
      test1: 0,
      test2: 0,
      test3: 0,
      test4: 0,
      test5: 0
    };

    rq.candidatos.push(nuevo);
  }

  updateCandidate(codigo: string, candidate: any) {
    const rq = this.getByCodigo(codigo);
    if (!rq) {
      return;
    }

    const existing = rq.candidatos.find((c: any) => c.id === candidate.id);
    if (!existing) {
      return;
    }

    Object.assign(existing, candidate);
  }

  getSelectedCandidates(codigo: string) {
    const rq = this.getByCodigo(codigo);
    if (!rq) {
      return [];
    }

    return rq.candidatos.filter((candidate: any) => candidate.elegido);
  }

  getResultsCandidates(codigo: string) {
    const rq = this.getByCodigo(codigo);
    if (!rq) {
      return [];
    }

    return rq.candidatos.filter((candidate: any) => candidate.apto && candidate.entrevistaAprobada);
  }

  updateRq(codigo: string, rq: any) {
    const existing = this.rqs.find((r) => r.codigo === codigo);
    if (!existing) {
      return;
    }
    Object.assign(existing, rq);
  }

  getAptosAprobados(codigo: string) {
    const rq = this.getByCodigo(codigo);
    if (!rq) {
      return [];
    }

    return rq.candidatos.filter(
      (candidate: any) => candidate.apto && candidate.entrevistaAprobada
    );
  }
}



