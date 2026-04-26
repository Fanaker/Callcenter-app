import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { RqService } from '../../../services/rq';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CandidatosListadoComponent } from '../candidatos-listado/candidatos-listado.component';

@Component({
  selector: 'app-reclutamiento-candidatos',
  standalone: true,
  imports: [CommonModule, FormsModule, CandidatosListadoComponent],
  templateUrl: './reclutamiento-candidatos.html',
  styleUrl: './reclutamiento-candidatos.css'
})
export class ReclutamientoCandidatos implements OnInit {
  rq: any;
  message = '';
  selectedCandidate: any = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rqService: RqService
  ) {}

  ngOnInit() {
    const codigo = this.route.snapshot.paramMap.get('codigo');
    if (codigo) {
      this.rq = this.rqService.getByCodigo(codigo);
    }
  }

  copyApplyLink() {
    const link = `${window.location.origin}/postular/${this.rq.codigo}`;
    navigator.clipboard.writeText(link).then(() => {
      this.message = 'Link copiado al portapapeles';
    });
  }

  openApplyLink() {
    const link = `${window.location.origin}/postular/${this.rq.codigo}`;
    window.open(link, '_blank');
  }

  verDetallePostulante(candidate: any) {
    this.selectedCandidate = candidate;
  }

  openCv(url: string) {
    window.open(url, '_blank');
  }

  getAllCandidates() {
    return this.rq?.candidatos || [];
  }
}
