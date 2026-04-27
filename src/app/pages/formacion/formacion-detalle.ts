import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
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
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';
  filterDni: string = '';
  filterNombre: string = '';
  filterApellido: string = '';

  constructor(
    private route: ActivatedRoute,
    private rqService: RqService
  ) {
    const codigo = this.route.snapshot.paramMap.get('codigo') || '';
    this.rq = this.rqService.getByCodigo(codigo);
  }

  getTestIndexes() {
    const count = this.rq?.testCount || 1;
    return Array.from({ length: Math.min(Math.max(count, 1), 5) }, (_, index) => index + 1);
  }

  getFilteredCandidates() {
    if (!this.rq?.candidatos) return [];
    return this.rq.candidatos.filter((candidato: any) => {
      const dniMatch = !this.filterDni || candidato.dni.toString().includes(this.filterDni);
      const nombreMatch = !this.filterNombre || candidato.nombre.toLowerCase().includes(this.filterNombre.toLowerCase());
      const apellidoMatch = !this.filterApellido || candidato.apellido.toLowerCase().includes(this.filterApellido.toLowerCase());
      return dniMatch && nombreMatch && apellidoMatch;
    }).sort((a: any, b: any) => {
      if (!this.sortColumn) return 0;
      let aValue = a[this.sortColumn];
      let bValue = b[this.sortColumn];
      if (this.sortColumn === 'promedio') {
        aValue = parseFloat(this.getAverage(a));
        bValue = parseFloat(this.getAverage(b));
      } else if (this.sortColumn === 'resultado') {
        aValue = this.isApproved(a) ? 1 : 0;
        bValue = this.isApproved(b) ? 1 : 0;
      }
      if (aValue < bValue) return this.sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return this.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
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
}
