import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { RqService } from '../../services/rq';
import { Rq } from '../../models/rq.model';
import { Postulante } from '../../models/postulante.model';

type SortField = 'dni' | 'nombre' | 'apellido' | 'promedio';
type ApprovalFilter = 'todos' | 'aprobados' | 'no-aprobados';
type TestField = 'test1' | 'test2' | 'test3' | 'test4' | 'test5';

@Component({
  selector: 'app-formacion-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './formacion-detalle.html',
  styleUrl: './formacion-detalle.css'
})
export class FormacionDetalle {
  rq: Rq | undefined;
  message = '';
  approvalFilter: ApprovalFilter = 'todos';
  sortColumn: SortField | '' = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rqService: RqService
  ) {
    const codigo = this.route.snapshot.paramMap.get('codigo') || '';
    this.rq = this.rqService.getByCodigo(codigo);
  }

  goBack(): void {
    this.router.navigate(['/formacion']);
  }

  getTrainingCandidates(): Postulante[] {
    if (!this.rq?.candidatos) {
      return [];
    }

    return this.rq.candidatos.filter(
      (candidate) => candidate.apto && candidate.entrevistaAprobada
    );
  }

  getFilteredAndSortedCandidates(): Postulante[] {
    let filtered = [...this.getTrainingCandidates()];

    if (this.approvalFilter === 'aprobados') {
      filtered = filtered.filter((candidate) => this.isApproved(candidate));
    }

    if (this.approvalFilter === 'no-aprobados') {
      filtered = filtered.filter((candidate) => !this.isApproved(candidate));
    }

    const sortColumn = this.sortColumn;

    if (sortColumn === '') {
      return filtered;
    }

    filtered.sort((a, b) => {
      let result = 0;

      if (sortColumn === 'promedio') {
        result = Number(this.getAverage(a)) - Number(this.getAverage(b));
      } else {
        const aValue = String(a[sortColumn] || '').toLowerCase();
        const bValue = String(b[sortColumn] || '').toLowerCase();
        result = aValue.localeCompare(bValue);
      }

      return this.sortDirection === 'asc' ? result : -result;
    });

    return filtered;
  }

  sortBy(column: SortField): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      return;
    }

    this.sortColumn = column;
    this.sortDirection = 'asc';
  }

  getSafeTestCount(): number {
    const count = Number(this.rq?.testCount || 1);

    if (count < 1) {
      return 1;
    }

    if (count > 5) {
      return 5;
    }

    return count;
  }

  getTestIndexes(): number[] {
    return Array.from({ length: this.getSafeTestCount() }, (_, index) => index + 1);
  }

  getTestField(index: number): TestField {
    return `test${index}` as TestField;
  }

  getTestValue(candidate: Postulante, index: number): number {
    const field = this.getTestField(index);
    return Number(candidate[field] || 0);
  }

  setTestValue(candidate: Postulante, index: number, value: string | number): void {
    const field = this.getTestField(index);
    let note = Number(value);

    if (Number.isNaN(note)) {
      note = 0;
    }

    if (note < 0) {
      note = 0;
    }

    if (note > 20) {
      note = 20;
    }

    candidate[field] = note;
  }

  getAverage(candidate: Postulante): string {
    const testIndexes = this.getTestIndexes();

    if (testIndexes.length === 0) {
      return '0.0';
    }

    const sum = testIndexes.reduce(
      (total, index) => total + this.getTestValue(candidate, index),
      0
    );

    return (sum / testIndexes.length).toFixed(1);
  }

  isApproved(candidate: Postulante): boolean {
    const average = Number(this.getAverage(candidate));
    const approvalNote = Number(this.rq?.aprobacionPromedio || 0);

    return average >= approvalNote;
  }

  getApprovedCount(): number {
    return this.getTrainingCandidates().filter(
      (candidate) => this.isApproved(candidate)
    ).length;
  }

  getNotApprovedCount(): number {
    return this.getTrainingCandidates().filter(
      (candidate) => !this.isApproved(candidate)
    ).length;
  }

  getResultLabel(candidate: Postulante): string {
    return this.isApproved(candidate) ? 'Aprobado' : 'No aprobado';
  }

  saveConfig(): void {
    if (!this.rq) {
      return;
    }

    this.rq.testCount = this.getSafeTestCount();

    if (this.rq.aprobacionPromedio < 0) {
      this.rq.aprobacionPromedio = 0;
    }

    if (this.rq.aprobacionPromedio > 20) {
      this.rq.aprobacionPromedio = 20;
    }

    this.rqService.updateRq(this.rq.codigo, {
      testCount: this.rq.testCount,
      aprobacionPromedio: this.rq.aprobacionPromedio
    });

    this.message = `Configuración de formación guardada para ${this.rq.codigo}.`;

    setTimeout(() => {
      this.message = '';
    }, 3000);
  }

  saveResults(): void {
    if (!this.rq) {
      return;
    }

    this.getTrainingCandidates().forEach((candidate) => {
      this.rqService.updateCandidate(this.rq!.codigo, candidate);
    });

    this.message = `Resultados de formación guardados para ${this.rq.codigo}.`;

    setTimeout(() => {
      this.message = '';
    }, 3000);
  }
}