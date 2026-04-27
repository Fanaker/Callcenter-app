import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RqService } from '../../services/rq';

@Component({
  selector: 'app-formacion',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './formacion.html',
  styleUrl: './formacion.css'
})
export class Formacion {
  rqs: any[] = [];
  statusFilter: string = 'todos';
  campaignFilter: string = '';
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  constructor(private rqService: RqService) {
    this.rqs = this.rqService.getAll();
  }

  sortBy(column: string) {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
  }

  get filteredAndSortedRqs() {
    let filtered = this.rqs;

    if (this.statusFilter !== 'todos') {
      filtered = filtered.filter(rq => rq.estado.toLowerCase() === this.statusFilter);
    }

    if (this.campaignFilter) {
      filtered = filtered.filter(rq => rq.campaign === this.campaignFilter);
    }

    if (this.sortColumn) {
      filtered.sort((a, b) => {
        let aVal = a[this.sortColumn];
        let bVal = b[this.sortColumn];
        let result = 0;

        if (this.sortColumn === 'fechaInicioCapacitacion' || this.sortColumn === 'fechaFinCapacitacion' || this.sortColumn === 'fechaIngreso') {
          result = new Date(aVal).getTime() - new Date(bVal).getTime();
        } else if (this.sortColumn === 'cantidad' || this.sortColumn === 'diasCapacitacion') {
          result = aVal - bVal;
        } else {
          result = aVal.localeCompare(bVal);
        }

        return this.sortDirection === 'asc' ? result : -result;
      });
    }

    return filtered;
  }

  get uniqueCampaigns() {
    return [...new Set(this.rqs.map(rq => rq.campaign))];
  }
}
