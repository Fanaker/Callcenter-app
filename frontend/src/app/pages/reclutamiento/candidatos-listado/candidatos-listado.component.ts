import {
  Component,
  OnInit,
  OnChanges,
  Input,
  Output,
  EventEmitter,
  SimpleChanges
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { Postulante } from '../../../models/postulante.model';

type FiltroCandidato = 'apto-si' | 'apto-no' | 'entrevista-si' | 'entrevista-no' | null;
type SortField = 'dni' | 'nombre' | 'apellido';

@Component({
  selector: 'app-candidatos-listado',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './candidatos-listado.component.html',
  styleUrls: ['./candidatos-listado.component.css']
})
export class CandidatosListadoComponent implements OnInit, OnChanges {
  @Input() candidatos: Postulante[] = [];
  @Output() verDetalle = new EventEmitter<Postulante>();

  candidatosFiltrados: Postulante[] = [];
  candidatosOriginales: Postulante[] = [];
  cargando = false;
  filtroActual: FiltroCandidato = null;
  sortField: SortField | '' = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  ngOnInit(): void {
    this.actualizarListado();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['candidatos']) {
      this.actualizarListado();
    }
  }

  private actualizarListado(): void {
    this.candidatosOriginales = [...(this.candidatos || [])];
    this.aplicarFiltro(this.filtroActual);
    this.aplicarOrdenamiento();
  }

  aplicarFiltro(filtro: FiltroCandidato): void {
    this.filtroActual = filtro;

    switch (filtro) {
      case 'apto-si':
        this.candidatosFiltrados = this.candidatosOriginales.filter(
          (candidato) => candidato.apto
        );
        break;

      case 'apto-no':
        this.candidatosFiltrados = this.candidatosOriginales.filter(
          (candidato) => !candidato.apto
        );
        break;

      case 'entrevista-si':
        this.candidatosFiltrados = this.candidatosOriginales.filter(
          (candidato) => candidato.entrevistaAprobada
        );
        break;

      case 'entrevista-no':
        this.candidatosFiltrados = this.candidatosOriginales.filter(
          (candidato) => !candidato.entrevistaAprobada
        );
        break;

      default:
        this.candidatosFiltrados = [...this.candidatosOriginales];
        break;
    }

    this.aplicarOrdenamiento();
  }

  sortBy(field: SortField): void {
    if (this.sortField === field) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortField = field;
      this.sortDirection = 'asc';
    }

    this.aplicarOrdenamiento();
  }

  private aplicarOrdenamiento(): void {
    if (!this.sortField) {
      return;
    }

    this.candidatosFiltrados.sort((a, b) => {
      const aValue = String(a[this.sortField as SortField] || '').toLowerCase();
      const bValue = String(b[this.sortField as SortField] || '').toLowerCase();

      if (this.sortDirection === 'asc') {
        return aValue.localeCompare(bValue);
      }

      return bValue.localeCompare(aValue);
    });
  }

  puedeMarcarEntrevista(candidato: Postulante): boolean {
    return candidato.apto;
  }

  cambiarApto(candidato: Postulante, valor: boolean): void {
    candidato.apto = valor;

    if (!valor) {
      candidato.entrevistaAprobada = false;
      candidato.elegido = false;
      candidato.contratar = false;
    }

    this.aplicarFiltro(this.filtroActual);
  }

  cambiarEntrevista(candidato: Postulante, valor: boolean): void {
    if (valor && !candidato.apto) {
      return;
    }

    candidato.entrevistaAprobada = valor;

    if (!valor) {
      candidato.elegido = false;
      candidato.contratar = false;
    }

    this.aplicarFiltro(this.filtroActual);
  }

  verDetalleCandidato(candidato: Postulante): void {
    this.verDetalle.emit(candidato);
  }

  contarApto(valor: boolean): number {
    return this.candidatosOriginales.filter(
      (candidato) => candidato.apto === valor
    ).length;
  }

  contarEntrevista(valor: boolean): number {
    return this.candidatosOriginales.filter(
      (candidato) => candidato.entrevistaAprobada === valor
    ).length;
  }
}