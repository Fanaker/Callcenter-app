import { Component, OnInit, OnChanges, Input, Output, EventEmitter, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Candidato } from '../models/candidato.model';

/**
 * Componente para listar todos los candidatos
 * Permite filtrar y ver detalles de candidatos exportados
 */
@Component({
  selector: 'app-candidatos-listado',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './candidatos-listado.component.html',
  styleUrls: ['./candidatos-listado.component.css']
})
export class CandidatosListadoComponent implements OnInit, OnChanges {
  @Input() candidatos: Candidato[] = [];
  @Output() verDetalle = new EventEmitter<Candidato>();

  candidatosFiltrados: Candidato[] = [];
  candidatosOriginales: Candidato[] = [];
  cargando = false;
  filtroActual: string | null = null;

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
    this.cargando = false;
  }

  /**
   * Aplica un filtro a la tabla
   */
  aplicarFiltro(filtro: string | null): void {
    this.filtroActual = filtro;

    switch (filtro) {
      case 'apto-si':
        this.candidatosFiltrados = this.candidatosOriginales.filter(c => c.apto === 'si');
        break;
      case 'apto-no':
        this.candidatosFiltrados = this.candidatosOriginales.filter(c => c.apto === 'no');
        break;
      case 'entrevista-si':
        this.candidatosFiltrados = this.candidatosOriginales.filter(c => c.entrevista === 'si');
        break;
      default:
        this.candidatosFiltrados = [...this.candidatosOriginales];
    }
  }

  /**
   * Verifica si se puede marcar entrevista (solo si apto = 'si')
   */
  puedeMarcarEntrevista(candidato: Candidato): boolean {
    return candidato.apto === 'si';
  }

  /**
   * Cambia el valor del campo Apto y ajusta entrevista si es necesario
   */
  cambiarApto(candidato: Candidato, valor: 'si' | 'no'): void {
    candidato.apto = valor;
    if (valor === 'no') {
      candidato.entrevista = 'no';
    }
    this.aplicarFiltro(this.filtroActual);
  }

  /**
   * Cambia el valor del campo Entrevista (con validación)
   */
  cambiarEntrevista(candidato: Candidato, valor: 'si' | 'no'): void {
    if (valor === 'si' && candidato.apto !== 'si') {
      return;
    }
    candidato.entrevista = valor;
  }

  /**
   * Muestra el detalle del candidato
   */
  verDetalleCandidato(candidato: Candidato): void {
    this.verDetalle.emit(candidato);
  }

  /**
   * Cuenta candidatos aptos
   */
  contarApto(valor: 'si' | 'no'): number {
    return this.candidatosOriginales.filter(c => c.apto === valor).length;
  }

  /**
   * Cuenta candidatos con resultado de entrevista
   */
  contarEntrevista(valor: 'si' | 'no'): number {
    return this.candidatosOriginales.filter(c => c.entrevista === valor).length;
  }

  /**
   * Obtiene el color para el chip de estado
   */
  obtenerColorEstado(estado: string): string {
    switch (estado) {
      case 'finalizado':
        return 'accent';
      case 'en_evaluacion':
        return 'warn';
      default:
        return '';
    }
  }
}