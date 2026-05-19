import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { RqService } from '../../services/rq';
import { Rq } from '../../models/rq.model';
import { Postulante, MedioPreferido } from '../../models/postulante.model';

type SortField = 'dni' | 'nombre' | 'apellido' | 'correo' | 'telefono' | 'medioPreferido';

@Component({
  selector: 'app-rq-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rq-detalle.html',
  styleUrl: './rq-detalle.css'
})
export class RqDetalle {
  rq: Rq | undefined;
  message = '';
  sortField: SortField | '' = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rqService: RqService
  ) {
    const codigo = this.route.snapshot.paramMap.get('codigo') || '';
    this.rq = this.rqService.getByCodigo(codigo);
  }

  getApprovedCandidates(): Postulante[] {
    if (!this.rq) {
      return [];
    }

    const results = this.rq.candidatos.filter(
      (candidate) => candidate.apto && candidate.entrevistaAprobada
    );

    if (!this.sortField) {
      return results;
    }

    return [...results].sort((a, b) => {
      const aValue = String(a[this.sortField as SortField] || '').toLowerCase();
      const bValue = String(b[this.sortField as SortField] || '').toLowerCase();

      if (this.sortDirection === 'asc') {
        return aValue.localeCompare(bValue);
      }

      return bValue.localeCompare(aValue);
    });
  }

  getTotalApproved(): number {
    return this.getApprovedCandidates().length;
  }

  getTotalHired(): number {
    return this.getApprovedCandidates().filter(
      (candidate) => candidate.contratar
    ).length;
  }

  getTotalPendingDecision(): number {
    return this.getApprovedCandidates().filter(
      (candidate) => !candidate.contratar
    ).length;
  }

  sortBy(field: SortField): void {
    if (this.sortField === field) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      return;
    }

    this.sortField = field;
    this.sortDirection = 'asc';
  }

  saveCandidate(candidate: Postulante): void {
    if (!this.rq) {
      return;
    }

    this.rqService.updateCandidate(this.rq.codigo, candidate);
    this.message = `Decisión guardada para ${candidate.nombre} ${candidate.apellido}.`;

    setTimeout(() => {
      this.message = '';
    }, 3000);
  }

  getMedioPreferidoLabel(medio: MedioPreferido): string {
    switch (medio) {
      case 'whatsapp':
        return 'Whatsapp';
      case 'llamada':
        return 'Llamada';
      case 'email':
        return 'Email';
      default:
        return 'No disponible';
    }
  }

  goBack(): void {
    this.router.navigate(['/reclutamiento']);
  }
}