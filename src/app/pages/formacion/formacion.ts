import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { RqService } from '../../services/rq';
import { Rq } from '../../models/rq.model';
import { Postulante } from '../../models/postulante.model';

type SortField =
  | 'codigo'
  | 'campaign'
  | 'puesto'
  | 'cantidad'
  | 'fechaInicioCapacitacion'
  | 'fechaFinCapacitacion'
  | 'diasCapacitacion'
  | 'fechaIngreso';

@Component({
  selector: 'app-formacion',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './formacion.html',
  styleUrl: './formacion.css'
})
export class Formacion {
  rqs: Rq[] = [];
  statusFilter = 'todos';
  campaignFilter = '';
  sortColumn: SortField | '' = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  constructor(private rqService: RqService) {
    this.rqs = this.rqService.getAll();
  }

  sortBy(column: SortField): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      return;
    }

    this.sortColumn = column;
    this.sortDirection = 'asc';
  }

  get filteredAndSortedRqs(): Rq[] {
    let filtered = [...this.rqs];

    if (this.statusFilter !== 'todos') {
      filtered = filtered.filter(
        (rq) => rq.estado.toLowerCase() === this.statusFilter
      );
    }

    if (this.campaignFilter) {
      filtered = filtered.filter((rq) => rq.campaign === this.campaignFilter);
    }

    if (!this.sortColumn) {
      return filtered;
    }

    const sortColumn = this.sortColumn;

    filtered.sort((a, b) => {
      let result = 0;

      if (
        sortColumn === 'fechaInicioCapacitacion' ||
        sortColumn === 'fechaFinCapacitacion' ||
        sortColumn === 'fechaIngreso'
      ) {
        result =
          new Date(String(a[sortColumn])).getTime() -
          new Date(String(b[sortColumn])).getTime();
      } else if (sortColumn === 'cantidad' || sortColumn === 'diasCapacitacion') {
        result = Number(a[sortColumn] || 0) - Number(b[sortColumn] || 0);
      } else {
        result = String(a[sortColumn] || '').localeCompare(
          String(b[sortColumn] || '')
        );
      }

      return this.sortDirection === 'asc' ? result : -result;
    });

    return filtered;
  }

  get uniqueCampaigns(): string[] {
    return [...new Set(this.rqs.map((rq) => rq.campaign).filter(Boolean))];
  }

  getTotalRQs(): number {
    return this.rqs.length;
  }

  getActiveRQs(): number {
    return this.rqs.filter((rq) => rq.estado.toLowerCase() === 'abierto').length;
  }

  getTotalPersonalRequerido(): number {
    return this.rqs
      .filter((rq) => rq.estado.toLowerCase() === 'abierto')
      .reduce((sum, rq) => sum + (rq.cantidad || 0), 0);
  }

  getTrainingCandidates(rq: Rq): Postulante[] {
    return (rq.candidatos || []).filter(
      (candidate) => candidate.apto && candidate.entrevistaAprobada
    );
  }

  getTotalPostulantesFormacion(): number {
    return this.rqs.reduce(
      (sum, rq) => sum + this.getTrainingCandidates(rq).length,
      0
    );
  }

  getApprovedFormationCount(): number {
    return this.rqs.reduce((sum, rq) => {
      const approvalNote = Number(rq.aprobacionPromedio || 0);
      const testCount = this.getSafeTestCount(rq);

      const approved = this.getTrainingCandidates(rq).filter((candidate) => {
        const average = this.getCandidateAverage(candidate, testCount);
        return average >= approvalNote;
      }).length;

      return sum + approved;
    }, 0);
  }

  getSafeTestCount(rq: Rq): number {
    const count = Number(rq.testCount || 1);

    if (count < 1) {
      return 1;
    }

    if (count > 5) {
      return 5;
    }

    return count;
  }

  getCandidateAverage(candidate: Postulante, testCount: number): number {
    const tests = Array.from({ length: testCount }, (_, index) => index + 1);

    if (tests.length === 0) {
      return 0;
    }

    const sum = tests.reduce((total, index) => {
      const field = `test${index}` as keyof Postulante;
      return total + Number(candidate[field] || 0);
    }, 0);

    return sum / tests.length;
  }
}