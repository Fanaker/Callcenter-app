import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
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

  constructor(
    private route: ActivatedRoute,
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
    return this.rq.candidatos.filter((candidate: any) => candidate.apto && candidate.entrevistaAprobada);
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
}