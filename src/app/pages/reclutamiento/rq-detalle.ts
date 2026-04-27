import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { RqService } from '../../services/rq';

@Component({
  selector: 'app-rq-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rq-detalle.html',
  styleUrl: './rq-detalle.css'
})
export class RqDetalle {
  rq: any;
  message = '';
  applyUrl = '';
  sortField: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rqService: RqService
  ) {
    const codigo = this.route.snapshot.paramMap.get('codigo') || '';
    this.rq = this.rqService.getByCodigo(codigo);
    if (this.rq) {
      this.applyUrl = window.location.origin + this.rq.applyPath;
    }
  }

  getResults() {
    if (!this.rq) {
      return [];
    }
    let results = this.rq.candidatos.filter((candidate: any) => candidate.apto && candidate.entrevistaAprobada);

    if (this.sortField) {
      results.sort((a: any, b: any) => {
        let aValue = a[this.sortField] || '';
        let bValue = b[this.sortField] || '';

        const aStr = String(aValue).toLowerCase();
        const bStr = String(bValue).toLowerCase();

        if (this.sortDirection === 'asc') {
          return aStr.localeCompare(bStr);
        } else {
          return bStr.localeCompare(aStr);
        }
      });
    }

    return results;
  }

  sortBy(field: string) {
    if (this.sortField === field) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortField = field;
      this.sortDirection = 'asc';
    }
  }

  saveCandidate(candidate: any) {
    this.rqService.updateCandidate(this.rq.codigo, candidate);
    this.message = 'Cambios guardados correctamente';
  }

  copyApplyLink() {
    if (!this.applyUrl) {
      return;
    }

    navigator.clipboard
      .writeText(this.applyUrl)
      .then(() => {
        this.message = 'Link copiado al portapapeles';
      })
      .catch(() => {
        this.message = 'No se pudo copiar el link';
      });
  }

  openApplyLink() {
    if (!this.applyUrl) {
      return;
    }

    window.open(this.applyUrl, '_blank');
  }

  goBack() {
    this.router.navigate(['/reclutamiento']);
  }
}