import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { RqService } from '../../../services/rq';
import { Rq } from '../../../models/rq.model';
import { Postulante } from '../../../models/postulante.model';
import { CandidatosListadoComponent } from '../candidatos-listado/candidatos-listado.component';

@Component({
  selector: 'app-reclutamiento-candidatos',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, CandidatosListadoComponent],
  templateUrl: './reclutamiento-candidatos.html',
  styleUrl: './reclutamiento-candidatos.css'
})
export class ReclutamientoCandidatos implements OnInit {
  rq: Rq | undefined;
  message = '';
  selectedCandidate: Postulante | null = null;

  constructor(
    private route: ActivatedRoute,
    private rqService: RqService
  ) {}

  ngOnInit(): void {
    const codigo = this.route.snapshot.paramMap.get('codigo');

    if (codigo) {
      this.rq = this.rqService.getByCodigo(codigo);
    }
  }

  copyApplyLink(): void {
    if (!this.rq) {
      return;
    }

    const link = `${window.location.origin}/postular/${this.rq.codigo}`;

    navigator.clipboard.writeText(link).then(() => {
      this.message = 'Link de postulación copiado al portapapeles.';

      setTimeout(() => {
        this.message = '';
      }, 3000);
    });
  }

  openApplyLink(): void {
    if (!this.rq) {
      return;
    }

    const link = `${window.location.origin}/postular/${this.rq.codigo}`;
    window.open(link, '_blank');
  }

  verDetallePostulante(candidate: Postulante): void {
    this.selectedCandidate = candidate;
  }

  cerrarDetalle(): void {
    this.selectedCandidate = null;
  }

  openCv(url: string): void {
    if (!url) {
      return;
    }

    window.open(url, '_blank');
  }

  getAllCandidates(): Postulante[] {
    return this.rq?.candidatos || [];
  }

  getTotalCandidatos(): number {
    return this.getAllCandidates().length;
  }

  getCandidatosAptos(): number {
    return this.getAllCandidates().filter((candidate) => candidate.apto).length;
  }

  getEntrevistasAprobadas(): number {
    return this.getAllCandidates().filter(
      (candidate) => candidate.entrevistaAprobada
    ).length;
  }

  getContratados(): number {
    return this.getAllCandidates().filter((candidate) => candidate.contratar).length;
  }

  getMedioPreferidoLabel(medio: string): string {
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
}