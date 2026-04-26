import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { RqService } from '../../services/rq';

@Component({
  selector: 'app-planeamiento',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './planeamiento.html',
  styleUrl: './planeamiento.css'
})
export class Planeamiento {
  rqs: any[] = [];

  constructor(private rqService: RqService) {
    this.rqs = this.rqService.getAll();
  }

  getTotalRQs() {
    return this.rqs.length;
  }

  getActiveRQs() {
    return this.rqs.filter(rq => rq.estado === 'ABIERTO').length;
  }

  getTotalPostulantes() {
    const allDnis = this.rqs.flatMap(rq => rq.candidatos.map((c: any) => c.dni));
    return new Set(allDnis).size;
  }

  getContratados() {
    return this.rqs.flatMap(rq => rq.candidatos.filter((c: any) => c.contratar)).length;
  }
}