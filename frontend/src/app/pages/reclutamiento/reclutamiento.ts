import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { RqService } from '../../services/rq';
import { Rq } from '../../models/rq.model';

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
  selector: 'app-reclutamiento',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './reclutamiento.html',
  styleUrl: './reclutamiento.css'
})
export class Reclutamiento {
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

    const sortColumn = this.sortColumn;

    if (sortColumn === '') {
      return filtered;
    }

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

  getTotalPostulantes(): number {
    const allDnis = this.rqs.flatMap((rq) =>
      rq.candidatos ? rq.candidatos.map((candidate) => candidate.dni) : []
    );

    return new Set(allDnis).size;
  }

  getContratados(): number {
    return this.rqs.flatMap((rq) =>
      rq.candidatos
        ? rq.candidatos.filter((candidate) => candidate.contratar)
        : []
    ).length;
  }
}