import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { RqService } from '../../services/rq';

@Component({
  selector: 'app-formacion-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './formacion-detalle.html',
  styleUrl: './formacion.css'
})
export class FormacionDetalle {
  rq: any;
  message = '';
  approvalFilter: string = 'todos';
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rqService: RqService
  ) {
    const codigo = this.route.snapshot.paramMap.get('codigo') || '';
    this.rq = this.rqService.getByCodigo(codigo);
  }

  getTestIndexes() {
    const count = this.rq?.testCount || 1;
    return Array.from({ length: Math.min(Math.max(count, 1), 5) }, (_, index) => index + 1);
  }

  getFilteredAndSortedCandidates() {
    if (!this.rq?.candidatos) return [];
    let filtered = this.rq.candidatos;

    if (this.approvalFilter === 'aprobados') {
      filtered = filtered.filter((c: any) => this.isApproved(c));
    } else if (this.approvalFilter === 'no aprobados') {
      filtered = filtered.filter((c: any) => !this.isApproved(c));
    }

    if (this.sortColumn) {
      filtered.sort((a: any, b: any) => {
        let aVal: any, bVal: any;
        if (this.sortColumn === 'dni') {
          aVal = parseInt(a.dni);
          bVal = parseInt(b.dni);
        } else if (this.sortColumn === 'promedio') {
          aVal = parseFloat(this.getAverage(a));
          bVal = parseFloat(this.getAverage(b));
        } else {
          aVal = a[this.sortColumn];
          bVal = b[this.sortColumn];
        }
        let result = 0;
        if (typeof aVal === 'number') {
          result = aVal - bVal;
        } else {
          result = aVal.localeCompare(bVal);
        }
        return this.sortDirection === 'asc' ? result : -result;
      });
    }

    return filtered;
  }

  sortBy(column: string) {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
  }

  getAverage(candidate: any) {
    const testIndexes = this.getTestIndexes();
    const sum = testIndexes.reduce((total, index) => total + (candidate[`test${index}`] || 0), 0);
    const average = sum / testIndexes.length;
    return average.toFixed(1);
  }

  isApproved(candidate: any) {
    const average = parseFloat(this.getAverage(candidate));
    return average >= (this.rq?.aprobacionPromedio || 0);
  }

  saveConfig() {
    if (!this.rq) {
      return;
    }
    this.rqService.updateRq(this.rq.codigo, this.rq);
    this.message = 'Configuración guardada para ' + this.rq.codigo;
  }

  saveResults() {
    if (!this.rq) {
      return;
    }
    this.rq.candidatos.forEach((candidate: any) => {
      this.rqService.updateCandidate(this.rq.codigo, candidate);
    });
    this.message = 'Resultados guardados para ' + this.rq.codigo;
  }

  goBack() {
    this.router.navigate(['/formacion']);
  }
}
