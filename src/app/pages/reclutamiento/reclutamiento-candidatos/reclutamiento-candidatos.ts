import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { RqService } from '../../../services/rq';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-reclutamiento-candidatos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reclutamiento-candidatos.html',
  styleUrl: './reclutamiento-candidatos.css'
})
export class ReclutamientoCandidatos implements OnInit {
  rq: any;
  message = '';

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

  saveCandidate(candidate: any) {
    this.rqService.updateCandidate(this.rq.codigo, candidate);
    this.message = 'Candidato guardado';
  }

  getAllCandidates() {
    return this.rq?.candidatos || [];
  }
}
