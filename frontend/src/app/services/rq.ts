import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Rq } from '../models/rq.model';
import { Postulante } from '../models/postulante.model';
import { Campania } from '../models/campania.model';
import { Puesto } from '../models/puesto.model';

@Injectable({
  providedIn: 'root'
})
export class RqService {
  private apiBaseUrl = 'http://localhost:3000/api';
  private apiUrl = `${this.apiBaseUrl}/requerimientos`;
  private rqs: Rq[] = [];

  constructor(private http: HttpClient) {}

  loadAll(): Observable<Rq[]> {
    return this.http.get<Rq[]>(this.apiUrl).pipe(
      tap((rqs) => {
        this.rqs = rqs.map((rq) => ({
          ...rq,
          estado: rq.estado || this.calcularEstadoRq(rq.fechaInicioCapacitacion),
          candidatos: rq.candidatos || []
        }));
      })
    );
  }

  getAll(): Rq[] {
    for (const rq of this.rqs) {
      rq.estado = rq.estado || this.calcularEstadoRq(rq.fechaInicioCapacitacion);
    }

    return this.rqs;
  }

  getByCodigo(codigo: string): Rq | undefined {
    const rq = this.rqs.find((rqItem) => rqItem.codigo === codigo);

    if (rq) {
      rq.estado = this.calcularEstadoRq(rq.fechaInicioCapacitacion);
    }

    return rq;
  }

  add(rq: Partial<Rq>): Observable<Rq> {
    return this.http.post<Rq>(this.apiUrl, rq).pipe(
      tap((nuevoRq) => {
        this.rqs.unshift({
          ...nuevoRq,
          candidatos: nuevoRq.candidatos || []
        });
      })
    );
  }

  updateRq(codigo: string, rq: Partial<Rq>): void {
    const existing = this.rqs.find((r) => r.codigo === codigo);

    if (!existing) {
      return;
    }

    Object.assign(existing, rq);
    existing.estado = this.calcularEstadoRq(existing.fechaInicioCapacitacion);
  }

  generateCode(): string {
    let max = 0;

    for (const rq of this.rqs) {
      const num = parseInt(rq.codigo.replace('RQ', ''), 10);
      if (num > max) {
        max = num;
      }
    }

    return 'RQ' + String(max + 1).padStart(3, '0');
  }

  addCandidate(codigo: string, candidate: Partial<Postulante>): void {
    const rq = this.getByCodigo(codigo);

    if (!rq || rq.estado === 'CERRADO') {
      return;
    }

    const nuevo: Postulante = {
      id: Date.now(),
      rqCodigo: codigo,
      nombre: candidate.nombre || '',
      apellido: candidate.apellido || '',
      dni: candidate.dni || '',
      correo: candidate.correo || '',
      telefono: candidate.telefono || '',
      medioPreferido: candidate.medioPreferido || 'whatsapp',
      cvUrl: candidate.cvUrl || '',
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

  updateCandidate(codigo: string, candidate: Partial<Postulante> & { id: number }): void {
    const rq = this.getByCodigo(codigo);

    if (!rq) {
      return;
    }

    const existing = rq.candidatos.find((c) => c.id === candidate.id);

    if (!existing) {
      return;
    }

    Object.assign(existing, candidate);
  }

  getSelectedCandidates(codigo: string): Postulante[] {
    const rq = this.getByCodigo(codigo);

    if (!rq) {
      return [];
    }

    return rq.candidatos.filter((candidate) => candidate.elegido);
  }

  getResultsCandidates(codigo: string): Postulante[] {
    const rq = this.getByCodigo(codigo);

    if (!rq) {
      return [];
    }

    return rq.candidatos.filter(
      (candidate) => candidate.apto && candidate.entrevistaAprobada
    );
  }

  getAptosAprobados(codigo: string): Postulante[] {
    const rq = this.getByCodigo(codigo);

    if (!rq) {
      return [];
    }

    return rq.candidatos.filter(
      (candidate) => candidate.apto && candidate.entrevistaAprobada
    );
  }

  getCampaniasActivas(): Observable<Campania[]> {
    return this.http.get<Campania[]>(`${this.apiBaseUrl}/campanias`);
  }

  getPuestosActivos(): Observable<Puesto[]> {
    return this.http.get<Puesto[]>(`${this.apiBaseUrl}/puestos`);
  }

  calcularEstadoRq(fechaInicioCapacitacion: string): 'ABIERTO' | 'CERRADO' {
    if (!fechaInicioCapacitacion) {
      return 'ABIERTO';
    }

    const hoy = new Date();
    const fechaInicio = new Date(fechaInicioCapacitacion);

    hoy.setHours(0, 0, 0, 0);
    fechaInicio.setHours(0, 0, 0, 0);

    return fechaInicio > hoy ? 'ABIERTO' : 'CERRADO';
  }
}
